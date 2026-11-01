"""Shared helpers for database utility modules."""
from typing import Any


def clean_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must not be empty")
    return value.strip()


def ensure_customer(connection: Any, name: str, shop_id: int) -> int:
    connection.execute(
        "INSERT INTO customers (name, shop_id) VALUES (?, ?) "
        "ON CONFLICT(shop_id, name) DO NOTHING",
        (name, shop_id),
    )
    row = connection.execute(
        "SELECT id FROM customers WHERE name = ? COLLATE NOCASE AND shop_id = ?",
        (name, shop_id),
    ).fetchone()
    return int(row["id"])
