"""Authentication dependencies for protected dashboard and agent routes."""

from typing import Any

from fastapi import HTTPException, Request, status

from .services import SESSION_COOKIE, get_user_for_session


def get_current_user(request: Request) -> dict[str, Any]:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")
    user = get_user_for_session(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired; sign in again")
    return user
