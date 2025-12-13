from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

from core.config import settings

async def get_api_key(api_key_header: str = Security(api_key_header)):
    expected_api_key = settings.API_KEY
    
    # If no API key is set in environment, allow access (or fail safe, user choice)
    # For security, we should probably block if not set, but for ease of dev maybe warn?
    # Let's block if not set to be safe.
    if not expected_api_key:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: API_KEY not set"
        )

    if api_key_header == expected_api_key:
        return api_key_header
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )
