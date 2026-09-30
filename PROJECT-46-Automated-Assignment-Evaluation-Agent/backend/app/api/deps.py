from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.security import decode_access_token
from backend.app.core.errors import UnauthorizedException, ForbiddenException
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Validate Bearer token and fetch the authenticated User."""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException("Invalid or expired authentication token.")

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise UnauthorizedException("User associated with this token does not exist.")
    if not user.is_active:
        raise ForbiddenException("User account is deactivated.")
    return user


def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    """Assert that the current user has TEACHER or ADMIN privileges."""
    if current_user.role not in (UserRole.TEACHER, UserRole.ADMIN):
        raise ForbiddenException("This resource is restricted to Teachers and Administrators.")
    return current_user


def require_student(current_user: User = Depends(get_current_user)) -> User:
    """Assert that the current user has STUDENT privileges."""
    return current_user
