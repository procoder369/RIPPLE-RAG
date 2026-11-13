"""Authentication and service security module."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import get_settings

security_bearer = HTTPBearer(auto_error=False)
settings = get_settings()


def verify_service_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> bool:
    """Verifies that requests from the main application contain the valid service token."""
    # In development mode, allow transparent access when testing without headers
    if settings.ENVIRONMENT == "development" and not credentials:
        return True

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header (Bearer token required)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.credentials != settings.SERVICE_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service authentication token",
        )

    return True

