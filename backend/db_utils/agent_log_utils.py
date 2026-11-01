"""Database operations for the agent activity log."""

from pathlib import Path
from typing import Any

from ..database import DEFAULT_DB_PATH, get_connection


def insert_agent_log(connection: Any, user_id: int, action: str, description: str) -> None:
    """Insert a log using the caller's transaction."""
    connection.execute(
        "INSERT INTO agent_logs (user_id, action, description) VALUES (?, ?, ?)",
        (user_id, action, description),
    )


def get_agent_logs(
    user_id: int,
    limit: int = 100,
    offset: int = 0,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT id, action, description, created_at
               FROM agent_logs WHERE user_id = ?
               ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?""",
            (user_id, limit, offset),
        ).fetchall()
    return [dict(row) for row in rows]
