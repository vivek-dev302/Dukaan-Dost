"""Google account and application-session operations."""

import hashlib
import os
import secrets
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token
from sqlalchemy import delete, func, select

from ..database import SessionLocal
from ..models import AuthSession, Category, Shop, User

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

SESSION_COOKIE = "dukaandost_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 14


def verify_google_credential(credential: str) -> dict[str, Any]:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")
    claims = id_token.verify_oauth2_token(credential, GoogleRequest(), client_id)
    if not claims.get("sub") or not claims.get("email") or not claims.get("email_verified"):
        raise ValueError("Google account must have a verified email address")
    return claims


def get_or_create_user(claims: dict[str, Any]) -> dict[str, Any]:
    google_sub = str(claims["sub"])
    email = str(claims["email"])
    name = str(claims.get("name") or email)
    picture = str(claims.get("picture") or "")

    with SessionLocal.begin() as session:
        session.execute(
            select(func.pg_advisory_xact_lock(func.hashtextextended(google_sub, 0)))
        )
        user = session.scalar(select(User).where(User.google_sub == google_sub))
        if user is None:
            shop = Shop(name=f"{name}'s Shop")
            session.add(shop)
            session.flush()
            session.add(Category(shop_id=shop.id, name="Other"))
            user = User(
                google_sub=google_sub,
                email=email,
                name=name,
                picture=picture,
                shop_id=shop.id,
            )
            session.add(user)
            session.flush()
        else:
            user.email = email
            user.name = name
            user.picture = picture

        result = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "shop_id": user.shop_id,
        }
    return result


def create_session(user_id: int) -> tuple[str, int]:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + SESSION_TTL_SECONDS
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with SessionLocal.begin() as session:
        session.execute(delete(AuthSession).where(AuthSession.expires_at <= int(time.time())))
        session.add(
            AuthSession(
                token_hash=token_hash,
                user_id=user_id,
                expires_at=expires_at,
                created_at=int(time.time()),
            )
        )
    return token, expires_at


def get_user_for_session(token: str) -> dict[str, Any] | None:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with SessionLocal() as session:
        row = session.execute(
            select(User.id, User.email, User.name, User.picture, User.shop_id)
            .join(AuthSession, AuthSession.user_id == User.id)
            .where(
                AuthSession.token_hash == token_hash,
                AuthSession.expires_at > int(time.time()),
            )
        ).mappings().first()
    return dict(row) if row else None


def revoke_session(token: str) -> None:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with SessionLocal.begin() as session:
        session.execute(delete(AuthSession).where(AuthSession.token_hash == token_hash))
