"""Category and catalog item database operations."""
from pathlib import Path
from typing import Any

from ..database import DEFAULT_DB_PATH, get_connection
from ._helpers import clean_text


def get_all_categories(shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT id, name FROM categories WHERE shop_id = ? ORDER BY name", (shop_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def add_category(name: str, shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO categories (name, shop_id) VALUES (?, ?)",
            (clean_text(name, "Category name"), shop_id),
        )
        return int(cursor.lastrowid)


def delete_category(category_id: int, shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    with get_connection(db_path) as connection:
        category = connection.execute(
            "SELECT name FROM categories WHERE id = ? AND shop_id = ?", (category_id, shop_id)
        ).fetchone()
        if category is None:
            return False
        if category["name"].casefold() == "other":
            raise ValueError("The default Other category cannot be deleted")
        used_by_catalog = connection.execute(
            "SELECT 1 FROM items WHERE category_id = ? AND shop_id = ? LIMIT 1", (category_id, shop_id)
        ).fetchone()
        used_by_restock = connection.execute(
            "SELECT 1 FROM restock_items WHERE category_id = ? AND shop_id = ? LIMIT 1", (category_id, shop_id)
        ).fetchone()
        if used_by_catalog or used_by_restock:
            raise ValueError("Remove this category's catalog and restock items first")
        connection.execute("DELETE FROM categories WHERE id = ? AND shop_id = ?", (category_id, shop_id))
        return True


def get_all_items(shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT i.id, i.name, i.category_id, c.name AS category_name
               FROM items i JOIN categories c ON c.id = i.category_id AND c.shop_id = i.shop_id
               WHERE i.shop_id = ? ORDER BY c.name, i.name""", (shop_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_items_by_category(category_id: int, shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT i.id, i.name, i.category_id, c.name AS category_name
               FROM items i JOIN categories c ON c.id = i.category_id AND c.shop_id = i.shop_id
               WHERE i.shop_id = ? AND i.category_id = ? ORDER BY i.name""",
            (shop_id, category_id),
        ).fetchall()
    return [dict(row) for row in rows]


def add_item(name: str, category_id: int, shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO items (name, category_id, shop_id) VALUES (?, ?, ?)",
            (clean_text(name, "Item name"), category_id, shop_id),
        )
        return int(cursor.lastrowid)


def delete_item(item_id: int, shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM items WHERE id = ? AND shop_id = ?", (item_id, shop_id))
        return cursor.rowcount > 0
