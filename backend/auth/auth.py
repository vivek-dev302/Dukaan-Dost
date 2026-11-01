"""Google sign-in and Dukaan Dost session API routes."""

import os

from fastapi import APIRouter, HTTPException, Request, Response, status
from starlette.concurrency import run_in_threadpool

from .dependencies import get_current_user
from .services import (
    SESSION_COOKIE,
    SESSION_TTL_SECONDS,
    create_session,
    get_or_create_user,
    revoke_session,
    verify_google_credential,
)
from .validators import GoogleCredential

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google")
async def login_with_google(data: GoogleCredential, response: Response):
    try:
        claims = await run_in_threadpool(verify_google_credential, data.credential)
        user = get_or_create_user(claims)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google credential") from exc

    token, _ = create_session(user["id"])
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=(os.getenv("APP_ENV", "development").lower() == "production"
                or os.getenv("SESSION_COOKIE_SAMESITE", "lax").lower() == "none"),
        samesite=os.getenv("SESSION_COOKIE_SAMESITE", "lax").lower(),
        max_age=SESSION_TTL_SECONDS,
        path="/",
    )
    return {"user": user}


@router.get("/me")
def current_user(request: Request):
    return get_current_user(request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        revoke_session(token)
    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
        httponly=True,
        secure=(os.getenv("APP_ENV", "development").lower() == "production"
                or os.getenv("SESSION_COOKIE_SAMESITE", "lax").lower() == "none"),
        samesite=os.getenv("SESSION_COOKIE_SAMESITE", "lax").lower(),
    )
