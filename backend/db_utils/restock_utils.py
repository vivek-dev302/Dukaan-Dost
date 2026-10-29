"""Restocking list database operations."""
from pathlib import Path
from typing import Any

from ..database import DEFAULT_DB_PATH, get_connection
from ._helpers import clean_text


def get_all_restock_items(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT r.id, r.name, r.category_id, c.name AS category_name
               FROM restock_items r JOIN categories c ON c.id = r.category_id
               ORDER BY c.name, r.name"""
        ).fetchall()
    return [dict(row) for row in rows]


def get_restock_items_by_category(
    category_id: int, db_path: str | Path = DEFAULT_DB_PATH
) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT r.id, r.name, r.category_id, c.name AS category_name
               FROM restock_items r JOIN categories c ON c.id = r.category_id
               WHERE r.category_id = ? ORDER BY r.name""",
            (category_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_restock_item(
    name: str, category_id: int, db_path: str | Path = DEFAULT_DB_PATH
) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO restock_items (name, category_id) VALUES (?, ?)",
            (clean_text(name, "Restock item name"), category_id),
        )
        return int(cursor.lastrowid)


def remove_restock_item(item_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "DELETE FROM restock_items WHERE id = ?", (item_id,)
        )
        return cursor.rowcount > 0


def delete_all_restock_items(db_path: str | Path = DEFAULT_DB_PATH) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM restock_items")
        return cursor.rowcount
