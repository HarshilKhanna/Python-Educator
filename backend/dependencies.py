"""
FastAPI dependency functions for authentication and role-based access control.

Usage
-----
    # Any authenticated user
    current_user: User = Depends(require_auth)

    # Instructor-only endpoints
    _: User = Depends(require_role("instructor"))
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth import decode_token
from database import get_db
from models import User

# FastAPI will look for "Authorization: Bearer <token>" on every request
# that uses this scheme.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def require_auth(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Resolve the current user from the JWT.

    Raises 401 if the token is missing, malformed, or expired.
    Raises 401 if the user ID from the token no longer exists in the DB.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise credentials_exc
    return user


def require_role(role: str):
    """
    Factory that returns a dependency requiring the authenticated user to have
    the specified role.

    Example::

        @router.get("/admin/data")
        async def admin_data(_: User = Depends(require_role("instructor"))):
            ...
    """
    async def _check_role(current_user: User = Depends(require_auth)) -> User:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: requires role '{role}', you have '{current_user.role}'.",
            )
        return current_user

    return _check_role
