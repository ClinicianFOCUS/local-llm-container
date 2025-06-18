"""
FastAPI proxy server for Ollama API with rate limiting and authentication.

This module implements a proxy server that forwards requests to an Ollama API instance,
adding authentication and rate limiting capabilities.
"""

import httpx
import asyncio
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from APIKeyManager import APIKeyManager
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Create a logger
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI()

# Initialize API key management
API_KEY_MANAGER = APIKeyManager()

# Print API key information and security warnings
print("\n" + "="*50)
print(" " * 5 + "⚠️ IMPORTANT: API Key Information ⚠️" + " " * 5)
print("="*50)
print("\n" + " " * 3 + f" Session API Key: {API_KEY_MANAGER.api_key} " + "\n")
print("="*50)
print("\nNOTE:")
print("- Do not share your API key publicly.")
print("- Avoid committing API keys in code repositories.")
print("- If exposed, reset and replace it immediately.\n")
print("="*50 + "\n")

#: str: The URL of the internal Ollama API service
OLLAMA_URL = "http://ollama:11434"

#: Limiter: Rate limiter instance configured with default limits
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1/second"]
)

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """
    Middleware for handling rate limiting of requests.
    
    :param request: The incoming HTTP request
    :type request: Request
    :param call_next: The next middleware or endpoint in the chain
    :type call_next: callable
    :return: HTTP response with rate limiting applied
    :rtype: Response
    """
    try:
        response = await call_next(request)
        return response
    except RateLimitExceeded:
        return PlainTextResponse(
            "Rate limit exceeded. Try again later.",
            status_code=429
        )

@app.get("/health")
@limiter.limit("1/second")
async def health_check(request: Request):
    """
    Health check endpoint to verify the service is running.
    
    :param request: The incoming HTTP request
    :type request: Request
    :return: JSON response indicating service status
    :rtype: JSONResponse
    """
    return JSONResponse(content={"status": "ok"})

@app.api_route("/{path:path}", methods=["GET", "POST"], dependencies=[Depends(API_KEY_MANAGER.verify_api_key)])
@limiter.limit("10/second")
async def proxy_request(path: str, request: Request):
    """
    Proxy endpoint that forwards requests to the Ollama API.
    
    Handles both GET and POST requests with proper client disconnection handling.
    
    :param path: The API path to forward to
    :type path: str
    :param request: The incoming HTTP request
    :type request: Request
    :return: Proxied response from Ollama API
    :rtype: JSONResponse
    """
    async with RequestHandler(request, path) as handler:
        return await handler.execute()
    
class RequestHandler:
    """
    Handles request forwarding and client disconnection monitoring.
    
    This class manages the lifecycle of HTTP requests forwarded to the Ollama API,
    including proper cleanup and client disconnection detection.
    """
    
    def __init__(self, request: Request, path: str):
        """
        Initialize the request handler.
        
        :param request: The FastAPI request object
        :type request: Request
        :param path: The API path to forward to
        :type path: str
        """
        self.request = request
        self.path = path
        self.client = None
        self.disconnect_event = asyncio.Event()
    
    async def __aenter__(self):
        """
        Async context manager entry point.
        
        :return: The RequestHandler instance
        :rtype: RequestHandler
        """
        timeout = httpx.Timeout(timeout=180.0, connect=10.0, read=180.0, write=180.0, pool=180.0)
        self.client = httpx.AsyncClient(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point.
        
        :param exc_type: Exception type if an exception occurred
        :type exc_type: type or None
        :param exc_val: Exception value if an exception occurred
        :type exc_val: Exception or None
        :param exc_tb: Exception traceback if an exception occurred
        :type exc_tb: traceback or None
        """
        if self.client:
            await self.client.aclose()
    
    async def listen_for_disconnect(self):
        """
        Listen for client disconnect events.
        
        Monitors the request stream for disconnect messages and sets the
        disconnect event when a disconnection is detected.
        """
        try:
            while not self.disconnect_event.is_set():
                message = await self.request.receive()
                if message.get("type") == "http.disconnect":
                    self.disconnect_event.set()
                    break
        except Exception:
            self.disconnect_event.set()
    
    async def check_client_disconnect(self):
        """
        Monitor client connection status.
        
        Periodically checks if the client is still connected and sets the
        disconnect event if a disconnection is detected.
        
        :return: True when client disconnects
        :rtype: bool
        """
        while not self.disconnect_event.is_set():
            if await self.request.is_disconnected():
                self.disconnect_event.set()
                return True
            await asyncio.sleep(0.1)
        return True
    
    def _filter_headers(self, headers):
        """
        Filter out problematic headers for forwarding.
        
        Removes headers that should not be forwarded to the upstream service
        to prevent conflicts or issues.
        
        :param headers: Original request headers
        :type headers: dict
        :return: Filtered headers safe for forwarding
        :rtype: dict
        """
        return {
            k: v for k, v in headers.items() 
            if k.lower() not in ['host', 'content-length', 'transfer-encoding']
        }
    
    async def _make_request(self):
        """
        Create the appropriate HTTP request based on method.
        
        Constructs and sends either a GET or POST request to the Ollama API
        with properly filtered headers and request data.
        
        :return: HTTP response from the Ollama API
        :rtype: httpx.Response
        """
        headers = self._filter_headers(self.request.headers)
        
        if self.request.method == "GET":
            return await self.client.get(
                f"{OLLAMA_URL}/{self.path}",
                headers=headers,
                params=self.request.query_params
            )
        elif self.request.method == "POST":
            body = await self.request.json()
            return await self.client.post(
                target_url,
                headers=headers,
                json=body
            )
    
    async def _handle_response(self, response):
        """
        Process the response from Ollama service.
        
        Converts the HTTP response to a JSONResponse, handling JSON parsing
        errors gracefully by falling back to text content.
        
        :param response: The HTTP response from Ollama
        :type response: httpx.Response
        :return: Formatted JSON response
        :rtype: JSONResponse
        """      
        try:
            response_content = response.json()
        except (ValueError, TypeError) as e:
            logger.exception(f"JSON decode error: {e}")
            response_content = response.text
        
        return JSONResponse(
            content=response_content,
            status_code=response.status_code
        )
    
    async def execute(self):
        """
        Execute the request with proper error handling and cancellation.
        
        Orchestrates the request forwarding process with concurrent monitoring
        for client disconnections. Handles various error conditions and ensures
        proper cleanup of resources.
        
        :return: HTTP response or error response
        :rtype: JSONResponse or HTTPException
        """
        try:
            # Set up concurrent tasks
            tasks = [
                asyncio.create_task(self._make_request()),
                asyncio.create_task(self.check_client_disconnect()),
                asyncio.create_task(self.listen_for_disconnect())
            ]
            
            # Wait for first completion
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            
            # Clean up cancelled tasks
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
            
            # Check results
            for task in done:
                if task == tasks[0]:  # Request task completed
                    try:
                        response = task.result()
                        return await self._handle_response(response)
                    except httpx.ReadError as e:
                        logger.exception(f"Read error from Ollama service: {e}")
                        return JSONResponse(
                            content={"error": "Connection error to Ollama service"},
                            status_code=502
                        )
                    except Exception as e:
                        logger.exception(f"Error getting response: {e}")
                        return JSONResponse(
                            content={"error": str(e)},
                            status_code=500
                        )
                else:  # Client disconnected
                    raise HTTPException(status_code=499, detail="Client disconnected")
            
            # Shouldn't reach here
            raise HTTPException(status_code=500, detail="Unexpected state")
            
        except asyncio.CancelledError as e:
            raise HTTPException(status_code=499, detail="Request cancelled") from e
        except httpx.ReadError as e:
            logger.exception(f"HTTP Read error: {e}")
            return JSONResponse(
                content={"error": "Connection error to Ollama service"},
                status_code=502
            )
        except httpx.TimeoutException:
            return JSONResponse(
                content={"error": "Request to Ollama service timed out"},
                status_code=504
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return JSONResponse(
                content={"error": str(e)},
                status_code=500
            )