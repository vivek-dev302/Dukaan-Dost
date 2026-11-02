"""Direct-SQL account and session operations."""

import hashlib
import os
import secrets
import time
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token
from dotenv import load_dotenv

from ..database import get_connection

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

    with get_connection() as connection:
        connection.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (google_sub,)
        )

        row = connection.execute(
            "SELECT id FROM users WHERE google_sub = %s",
            (google_sub,)
        ).fetchone()

        if row is not None:
            # Existing user: update profile information.
            user_id = int(row["id"])

            connection.execute(
                "UPDATE users SET email = %s, name = %s, picture = %s WHERE id = %s",
                (email, name, picture, user_id),
            )

        else:
            # New user: create a completely new, empty shop.
            row = connection.execute(
                "INSERT INTO shops (name) VALUES (%s) RETURNING id",
                (f"{name}'s Shop",),
            ).fetchone()
            shop_id = int(row["id"])

            # Create the default category for the new shop.
            connection.execute(
                "INSERT INTO categories (shop_id, name) VALUES (%s, 'Other')",
                (shop_id,),
            )

            # Create the user and associate the new shop.
            row = connection.execute(
                "INSERT INTO users (google_sub, email, name, picture, shop_id) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (google_sub, email, name, picture, shop_id),
            ).fetchone()

            user_id = int(row["id"])

        user = connection.execute(
            "SELECT id, email, name, picture, shop_id "
            "FROM users WHERE id = %s",
            (user_id,),
        ).fetchone()

        return dict(user)



def create_session(user_id: int) -> tuple[str, int]:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + SESSION_TTL_SECONDS
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with get_connection() as connection:
        connection.execute("DELETE FROM auth_sessions WHERE expires_at <= %s", (int(time.time()),))
        connection.execute(
            "INSERT INTO auth_sessions (token_hash, user_id, expires_at, created_at) "
            "VALUES (%s, %s, %s, %s)",
            (token_hash, user_id, expires_at, int(time.time())),
        )
    return token, expires_at


def get_user_for_session(token: str) -> dict[str, Any] | None:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with get_connection() as connection:
        row = connection.execute(
            """SELECT u.id, u.email, u.name, u.picture, u.shop_id
               FROM auth_sessions s JOIN users u ON u.id = s.user_id
               WHERE s.token_hash = %s AND s.expires_at > %s""",
            (token_hash, int(time.time())),
        ).fetchone()
    return dict(row) if row else None


def revoke_session(token: str) -> None:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with get_connection() as connection:
        connection.execute("DELETE FROM auth_sessions WHERE token_hash = %s", (token_hash,))
