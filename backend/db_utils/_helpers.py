"""Shared helpers for database utility modules."""
from typing import Any


def clean_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must not be empty")
    return value.strip()


def ensure_customer(connection: Any, name: str, shop_id: int) -> int:
    connection.execute(
        "INSERT INTO customers (name, shop_id) VALUES (%s, %s) "
        "ON CONFLICT DO NOTHING",
        (name, shop_id),
    )
    row = connection.execute(
        "SELECT id FROM customers WHERE lower(name) = lower(%s) AND shop_id = %s",
        (name, shop_id),
    ).fetchone()
    return int(row["id"])
