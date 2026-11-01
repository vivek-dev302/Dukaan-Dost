"""Customer database operations."""

from pathlib import Path
from typing import Any

from ..database import DEFAULT_DB_PATH, get_connection
from ._helpers import clean_text
from .agent_log_utils import insert_agent_log


def get_all_customers(shop_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT id, name, total_paise FROM customers WHERE shop_id = ? ORDER BY name",
            (shop_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_customer(
    name: str,
    shop_id: int,
    db_path: str | Path = DEFAULT_DB_PATH,
    *,
    agent_user_id: int | None = None,
) -> int:
    with get_connection(db_path) as connection:
        customer_name = clean_text(name, "Customer name")
        cursor = connection.execute(
            "INSERT INTO customers (name, shop_id) VALUES (?, ?)",
            (customer_name, shop_id),
        )
        customer_id = int(cursor.lastrowid)
        if agent_user_id is not None:
            insert_agent_log(
                connection, agent_user_id, "customer.added", f'Added customer "{customer_name}".'
            )
        return customer_id
