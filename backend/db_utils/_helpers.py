"""Shared helpers for database utility modules."""
from typing import Any


def clean_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must not be empty")
    return value.strip()


def ensure_customer(connection: Any, name: str) -> int:
    connection.execute(
        "INSERT INTO customers (name) VALUES (?) ON CONFLICT(name) DO NOTHING",
        (name,),
    )
    row = connection.execute(
        "SELECT id FROM customers WHERE name = ? COLLATE NOCASE", (name,)
    ).fetchone()
    return int(row["id"])
