"""
API Key Management Module
========================

Provides secure API key management functionality including generation,
storage, and validation of API keys for FastAPI applications.

The module implements a secure way to handle API key authentication using the 
HTTP Bearer scheme. It includes automatic key generation if none exists and
validation middleware for FastAPI routes.
"""

import os
import secrets
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class APIKeyManager:
    """
    A class to manage API key operations for FastAPI applications.
    
    This class handles the generation, storage, and validation of API keys.
    It uses environment variables for key storage and implements the HTTP
    Bearer authentication scheme for request validation.
    
    :ivar bearer_scheme: HTTPBearer instance for handling authentication
    :type bearer_scheme: HTTPBearer
    :ivar api_key: The current API key value
    :type api_key: str
    
    Example:
        >>> api_manager = APIKeyManager()
        >>> @app.get("/protected")
        >>> async def protected_route(token: str = Depends(api_manager.verify_api_key)):
        >>>     return {"message": "Access granted"}
    
    Note:
        The API key is automatically generated if none exists in the environment
        variables. The key is stored in the SESSION_API_KEY environment variable.
    """

    def __init__(self):
        """
        Initialize the API Key Manager.
        
        Sets up the HTTP Bearer scheme and either retrieves an existing API key
        from environment variables or generates a new one if none exists.
        
        The generated API key is 32 bytes long and URL-safe encoded.
        """
        self.bearer_scheme = HTTPBearer()
        self.api_key = os.getenv('SESSION_API_KEY')
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(32)
            os.environ['SESSION_API_KEY'] = self.api_key

    async def verify_api_key(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> str:
        """
        Verify the API key from incoming requests.
        
        This method is designed to be used as a FastAPI dependency injection.
        It validates the Bearer token against the stored API key.
        
        :param credentials: The credentials extracted from the Authorization header
        :type credentials: HTTPAuthorizationCredentials
        :returns: The verified API key if valid
        :rtype: str
        :raises HTTPException: If the API key is invalid or missing
            with status code 401
        
        Example:
            >>> @app.get("/protected")
            >>> async def protected(token: str = Depends(api_manager.verify_api_key)):
            >>>     return {"status": "authorized"}
        """
        if credentials.credentials == self.api_key:
            return credentials.credentials
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing Bearer Token",
        )