"""Database operations for the agent activity log."""

from typing import Any

from ..database import get_connection


def insert_agent_log(connection: Any, user_id: int, action: str, description: str) -> None:
    """Insert a log using the caller's transaction."""
    connection.execute(
        "INSERT INTO agent_logs (user_id, action, description) VALUES (%s, %s, %s)",
        (user_id, action, description),
    )


def get_agent_logs(
    user_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT id, action, description, created_at
               FROM agent_logs WHERE user_id = %s
               ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s""",
            (user_id, limit, offset),
        ).fetchall()
    return [dict(row) for row in rows]
