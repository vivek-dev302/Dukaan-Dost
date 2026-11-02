"""Restocking list database operations."""

from typing import Any

from ..database import get_connection
from ._helpers import clean_text
from .agent_log_utils import insert_agent_log


def get_all_restock_items(shop_id: int) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT r.id, r.name, r.category_id, c.name AS category_name
               FROM restock_items r JOIN categories c ON c.id = r.category_id AND c.shop_id = r.shop_id
               WHERE r.shop_id = %s ORDER BY c.name, r.name""", (shop_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_restock_items_by_category(category_id: int, shop_id: int) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT r.id, r.name, r.category_id, c.name AS category_name
               FROM restock_items r JOIN categories c ON c.id = r.category_id AND c.shop_id = r.shop_id
               WHERE r.shop_id = %s AND r.category_id = %s ORDER BY r.name""",
            (shop_id, category_id),
        ).fetchall()
    return [dict(row) for row in rows]


def add_restock_item(
    name: str,
    category_id: int,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> int:
    with get_connection() as connection:
        item_name = clean_text(name, "Restock item name")
        cursor = connection.execute(
            "INSERT INTO restock_items (name, category_id, shop_id) VALUES (%s, %s, %s) RETURNING id",
            (item_name, category_id, shop_id),
        )
        item_id = int(cursor.fetchone()["id"])
        if agent_user_id is not None:
            category = connection.execute(
                "SELECT name FROM categories WHERE id = %s AND shop_id = %s", (category_id, shop_id)
            ).fetchone()
            category_name = category["name"] if category else str(category_id)
            insert_agent_log(
                connection, agent_user_id, "restock_item.added",
                f'Added "{item_name}" to the restock list under "{category_name}".',
            )
        return item_id


def remove_restock_item(
    item_id: int,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> bool:
    with get_connection() as connection:
        item = connection.execute(
            "SELECT name FROM restock_items WHERE id = %s AND shop_id = %s", (item_id, shop_id)
        ).fetchone()
        cursor = connection.execute(
            "DELETE FROM restock_items WHERE id = %s AND shop_id = %s", (item_id, shop_id)
        )
        if cursor.rowcount and agent_user_id is not None:
            insert_agent_log(
                connection, agent_user_id, "restock_item.removed",
                f'Removed "{item["name"]}" from the restock list.',
            )
        return cursor.rowcount > 0


def delete_all_restock_items(
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> int:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM restock_items WHERE shop_id = %s", (shop_id,))
        if cursor.rowcount and agent_user_id is not None:
            insert_agent_log(
                connection, agent_user_id, "restock_list.cleared",
                f'Cleared {cursor.rowcount} item(s) from the restock list.',
            )
        return cursor.rowcount
