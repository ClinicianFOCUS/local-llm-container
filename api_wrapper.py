"""
FastAPI proxy server for Ollama API with rate limiting and authentication.

This module implements a proxy server that forwards requests to an Ollama API instance,
adding authentication and rate limiting capabilities.
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from APIKeyManager import APIKeyManager
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter

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

    This middleware intercepts all HTTP requests and enforces rate limiting rules.
    If a request exceeds the rate limit, it returns a 429 status code.

    Args:
        request (Request): The incoming FastAPI request object
        call_next (Callable): Function to call the next middleware or route handler

    Returns:
        Response: Either the normal response or a rate limit exceeded response

    Raises:
        RateLimitExceeded: When the request rate exceeds the defined limit
    """
    try:
        response = await call_next(request)
        return response
    except RateLimitExceeded:
        return PlainTextResponse(
            "Rate limit exceeded. Try again later.",
            status_code=429
        )

@app.api_route("/{path:path}", methods=["GET", "POST"], dependencies=[Depends(API_KEY_MANAGER.verify_api_key)])
@limiter.limit("10/second")
async def proxy_request(path: str, request: Request):
    """
    Proxy endpoint that forwards requests to the Ollama API.

    This endpoint handles both GET and POST requests, forwarding them to the
    corresponding Ollama API endpoint while maintaining headers and request body.

    Args:
        path (str): The path component of the URL to forward to Ollama
        request (Request): The incoming FastAPI request object

    Returns:
        JSONResponse: The response from the Ollama API, wrapped in a JSONResponse

    Raises:
        HTTPException: When there's an error processing the request
        JSONDecodeError: When the response from Ollama is not valid JSON
        Exception: For any other unexpected errors

    Examples:
        >>> # GET request
        >>> response = client.get("/api/v1/models")
        
        >>> # POST request
        >>> response = client.post("/api/v1/generate", json={"prompt": "Hello"})
    """
    try:
        headers = request.headers
        
        if request.method == "GET":
            response = requests.get(
                f"{OLLAMA_URL}/{path}",
                headers=headers,
                params=request.query_params
            )
        elif request.method == "POST":
            body = await request.json()
            response = requests.post(
                f"{OLLAMA_URL}/{path}",
                headers=headers,
                json=body
            )

        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except requests.exceptions.JSONDecodeError:
        return JSONResponse(
            content=response.text,
            status_code=response.status_code
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )