"""
FastAPI dependencies for authentication and database access
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.services.auth_service import AuthService
from app.models.user import User

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Extract and verify JWT token from Authorization header
    """
    token = credentials.credentials
    return verify_token(token)


def get_current_user(
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user_token)
) -> User:
    """
    Get current authenticated user from token
    """
    user = AuthService.get_user_by_id(db, token_data["user_id"])
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (alias for get_current_user for clarity)
    """
    return current_user


# Optional authentication - returns None if no token provided
def get_current_user_optional(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    """
    if not credentials:
        return None
    
    try:
        token_data = verify_token(credentials.credentials)
        user = AuthService.get_user_by_id(db, token_data["user_id"])
        
        if user and user.is_active:
            return user
    except HTTPException:
        pass
    
    return None