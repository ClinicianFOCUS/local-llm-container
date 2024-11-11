from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import os
import secrets

# Initialize the FastAPI app
app = FastAPI()

# Function to generate a secure API key
def generate_api_key():
    return secrets.token_urlsafe(32)

# Define the API key for authentication
API_KEY = os.getenv("SESSION_API_KEY", generate_api_key())

print("\n" + "="*50)
print(" " * 5 + "⚠️ IMPORTANT: API Key Information ⚠️" + " " * 5)
print("="*50)
print("\n" + " " * 3 + f" Session API Key: {API_KEY} " + "\n")
print("="*50)
print("\nNOTE:")
print("- Do not share your API key publicly.")
print("- Avoid committing API keys in code repositories.")
print("- If exposed, reset and replace it immediately.\n")
print("="*50 + "\n")

bearer_scheme = HTTPBearer()

# Set the URL of the internal Ollama API (using the service name defined in docker-compose.yml)
OLLAMA_URL = "http://ollama:11434"  # Docker will resolve "ollama" to the Ollama container's IP


# Function to retrieve and validate the API key from the request headers
def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    global API_KEY
    token = credentials.credentials
    if token == API_KEY:
        return token
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing Bearer Token",
    )

# Function to check and retrieve the API key from the environment variables
def check_api_key():
    api_key = os.getenv('SESSION_API_KEY')
    if not api_key:
        # If not found, generate a new one and store it in environment variables
        api_key = generate_api_key()
        os.environ['SESSION_API_KEY'] = api_key
    return api_key

# Function to get the client's IP address from request headers
def get_ip_from_headers(request: Request):
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0]
    return request.client.host

# Define the health endpoint without authentication
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Define proxy endpoint with authentication dependency
@app.api_route("/{path:path}", methods=["GET", "POST"], dependencies=[Depends(get_api_key)])
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
