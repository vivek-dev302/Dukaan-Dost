"""Category and catalog item database operations."""
from pathlib import Path
from typing import Any

from ..database import DEFAULT_DB_PATH, get_connection
from ._helpers import clean_text


def get_all_categories(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    return [dict(row) for row in rows]


def add_category(name: str, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO categories (name) VALUES (?)",
            (clean_text(name, "Category name"),),
        )
        return int(cursor.lastrowid)


def delete_category(category_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    with get_connection(db_path) as connection:
        category = connection.execute(
            "SELECT name FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        if category is None:
            return False
        if category["name"].casefold() == "other":
            raise ValueError("The default Other category cannot be deleted")
        used_by_catalog = connection.execute(
            "SELECT 1 FROM items WHERE category_id = ? LIMIT 1", (category_id,)
        ).fetchone()
        used_by_restock = connection.execute(
            "SELECT 1 FROM restock_items WHERE category_id = ? LIMIT 1", (category_id,)
        ).fetchone()
        if used_by_catalog or used_by_restock:
            raise ValueError("Remove this category's catalog and restock items first")
        connection.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        return True


def get_all_items(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT i.id, i.name, i.category_id, c.name AS category_name
               FROM items i JOIN categories c ON c.id = i.category_id
               ORDER BY c.name, i.name"""
        ).fetchall()
    return [dict(row) for row in rows]


def get_items_by_category(
    category_id: int, db_path: str | Path = DEFAULT_DB_PATH
) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT i.id, i.name, i.category_id, c.name AS category_name
               FROM items i JOIN categories c ON c.id = i.category_id
               WHERE i.category_id = ? ORDER BY i.name""",
            (category_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_item(
    name: str, category_id: int, db_path: str | Path = DEFAULT_DB_PATH
) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO items (name, category_id) VALUES (?, ?)",
            (clean_text(name, "Item name"), category_id),
        )
        return int(cursor.lastrowid)


def delete_item(item_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM items WHERE id = ?", (item_id,))
        return cursor.rowcount > 0
