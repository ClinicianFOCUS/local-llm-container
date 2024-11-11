"""
API Key Management Module
========================

This module provides secure API key management functionality including generation,
storage, and validation of API keys for FastAPI applications.

The module uses environment variables for persistent storage and implements
bearer token authentication.
"""

import os
import secrets
from typing import Optional
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class APIKeyManager:
    """
    A class to manage API key generation, storage, and validation.

    This class handles all aspects of API key management including:
    - Secure generation of API keys
    - Storage in environment variables
    - Validation of incoming API key requests
    - IP address extraction from requests

    Attributes
    ----------
    bearer_scheme : HTTPBearer
        FastAPI's HTTP Bearer authentication scheme
    _api_key : Optional[str]
        Private storage for the current API key
    api_key : str
        Property for accessing the current API key

    Example
    -------
    >>> api_manager = APIKeyManager()
    >>> current_key = api_manager.api_key
    >>> # In FastAPI route
    >>> @app.get("/protected")
    >>> async def protected_route(token: str = Depends(api_manager.verify_api_key)):
    >>>     return {"message": "Access granted"}
    """

    def __init__(self):
        """
        Initialize the APIKeyManager with a bearer scheme and API key.

        The constructor sets up the HTTP Bearer authentication scheme and
        initializes the API key either from environment variables or by
        generating a new one.
        """
        self.bearer_scheme = HTTPBearer()
        self._api_key: Optional[str] = None
        # Initialize the API key when the class is instantiated
        self.api_key = self.get_or_generate_api_key()

    @property
    def api_key(self) -> str:
        """
        Get the current API key.

        Returns
        -------
        str
            The current API key
        """
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        """
        Set the current API key.

        Parameters
        ----------
        value : str
            The new API key value to set
        """
        self._api_key = value

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a new secure API key.

        Returns
        -------
        str
            A URL-safe token string of 32 bytes

        Notes
        -----
        Uses secrets.token_urlsafe() for cryptographically secure
        token generation.
        """
        return secrets.token_urlsafe(32)

    def get_or_generate_api_key(self) -> str:
        """
        Retrieve existing API key or generate a new one.

        This method checks for an existing API key in environment variables.
        If none exists, it generates a new one and stores it.

        Returns
        -------
        str
            Either the existing or newly generated API key

        Notes
        -----
        The API key is stored in the 'SESSION_API_KEY' environment variable.
        """
        api_key = os.getenv('SESSION_API_KEY')
        if not api_key:
            # If not found, generate a new one and store it in environment variables
            api_key = self.generate_api_key()
            os.environ['SESSION_API_KEY'] = api_key
        return api_key

    async def verify_api_key(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> str:
        """
        Verify the API key from incoming requests.

        This method is designed to be used as a FastAPI dependency for
        protecting routes with API key authentication.

        Parameters
        ----------
        credentials : HTTPAuthorizationCredentials
            Credentials extracted from the Authorization header

        Returns
        -------
        str
            The validated API key token

        Raises
        ------
        HTTPException
            401 error if the API key is invalid or missing

        Example
        -------
        >>> @app.get("/protected")
        >>> async def protected_route(token: str = Depends(api_manager.verify_api_key)):
        >>>     return {"message": "Access granted"}
        """
        token = credentials.credentials
        if token == self.api_key:
            return token
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing Bearer Token",
        )

    @staticmethod
    def get_ip_from_headers(request: Request) -> str:
        """
        Extract the client IP address from request headers.

        This method attempts to get the real IP address of the client,
        taking into account proxy forwarding.

        Parameters
        ----------
        request : Request
            The FastAPI request object

        Returns
        -------
        str
            The client's IP address

        Notes
        -----
        Checks X-Forwarded-For header first, falls back to direct client IP
        if not available.
        """
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0]
        return request.client.host