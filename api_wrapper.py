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

# Define the API key for authentication
API_KEY_MANAGER = APIKeyManager()

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

# Set the URL of the internal Ollama API (using the service name defined in docker-compose.yml)
OLLAMA_URL = "http://ollama:11434"  # Docker will resolve "ollama" to the Ollama container's IP

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1/second"]
)

# Add middleware for rate limiting
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """
    This function adds middleware to an application for rate limiting HTTP requests. 
    It processes incoming requests and either forwards them for handling or returns a `429 Too Many Requests` 
    response if the rate limit is exceeded.

    Example:
    --------

    .. code-block:: python

        @app.middleware("http")
        async def rate_limit_middleware(request, call_next):
            try:
                response = await call_next(request)
                return response
            except RateLimitExceeded as e:
                logging.warning(f"Rate limit exceeded: {e}")
                return PlainTextResponse("Rate limit exceeded. Try again later.", status_code=429)

    Parameters:
    -----------
    - `request` : The incoming HTTP request.
    - `call_next` : Callable to pass the request to the next handler.

    Returns:
    --------
    - `response` : The HTTP response from the next handler in the middleware chain.
    - If the rate limit is exceeded, returns a `PlainTextResponse` with a 429 status code and a "Rate limit exceeded" message.

    Raises:
    -------
    - `RateLimitExceeded` : Raised when the request exceeds the allowed rate limit.
    """
    try:
        response = await call_next(request)
        return response
    except RateLimitExceeded:
        return PlainTextResponse(
            "Rate limit exceeded. Try again later.", status_code=429
        )

# Define proxy endpoint with authentication dependency
@app.api_route("/{path:path}", methods=["GET", "POST"], dependencies=[Depends(API_KEY_MANAGER.verify_api_key)])
@limiter.limit("1/second")
async def proxy_request(path: str, request: Request):
    try:
        # Prepare headers and body based on the request method
        headers = dict(request.headers)
        if request.method == "GET":
            response = requests.get(f"{OLLAMA_URL}/{path}", headers=headers, params=request.query_params)
        elif request.method == "POST":
            body = await request.json()
            response = requests.post(f"{OLLAMA_URL}/{path}", headers=headers, json=body)

        # Return the response from the Ollama API
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.exceptions.JSONDecodeError:
        return JSONResponse(content=response.text, status_code=response.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
