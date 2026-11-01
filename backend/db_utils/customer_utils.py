"""Customer database operations."""

from pathlib import Path
from typing import Any

from ..database import DEFAULT_DB_PATH, get_connection
from ._helpers import clean_text


def get_all_customers(shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT id, name, total_paise FROM customers WHERE shop_id = ? ORDER BY name",
            (shop_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_customer(name: str, shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO customers (name, shop_id) VALUES (?, ?)",
            (clean_text(name, "Customer name"), shop_id),
        )
        return int(cursor.lastrowid)
