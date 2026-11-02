"""Restocking list database operations."""

from typing import Any

from sqlalchemy import delete, select

from ..database import SessionLocal
from ..models import Category, RestockItem
from ._helpers import clean_text
from .agent_log_utils import insert_agent_log


def get_all_restock_items(shop_id: int) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(
                RestockItem.id,
                RestockItem.name,
                RestockItem.category_id,
                Category.name.label("category_name"),
            )
            .join(
                Category,
                (Category.id == RestockItem.category_id) & (Category.shop_id == RestockItem.shop_id),
            )
            .where(RestockItem.shop_id == shop_id)
            .order_by(Category.name, RestockItem.name)
        ).mappings().all()
    return [dict(row) for row in rows]


def get_restock_items_by_category(category_id: int, shop_id: int) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(
                RestockItem.id,
                RestockItem.name,
                RestockItem.category_id,
                Category.name.label("category_name"),
            )
            .join(
                Category,
                (Category.id == RestockItem.category_id) & (Category.shop_id == RestockItem.shop_id),
            )
            .where(RestockItem.shop_id == shop_id, RestockItem.category_id == category_id)
            .order_by(RestockItem.name)
        ).mappings().all()
    return [dict(row) for row in rows]


def add_restock_item(
    name: str,
    category_id: int,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> int:
    item_name = clean_text(name, "Restock item name")
    with SessionLocal.begin() as session:
        item = RestockItem(name=item_name, category_id=category_id, shop_id=shop_id)
        session.add(item)
        session.flush()
        if agent_user_id is not None:
            category_name = session.scalar(
                select(Category.name).where(Category.id == category_id, Category.shop_id == shop_id)
            ) or str(category_id)
            insert_agent_log(
                session,
                agent_user_id,
                "restock_item.added",
                f'Added "{item_name}" to the restock list under "{category_name}".',
            )
        return item.id


def remove_restock_item(
    item_id: int,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> bool:
    with SessionLocal.begin() as session:
        item = session.scalar(
            select(RestockItem).where(RestockItem.id == item_id, RestockItem.shop_id == shop_id)
        )
        if item is None:
            return False
        item_name = item.name
        session.delete(item)
        if agent_user_id is not None:
            insert_agent_log(
                session,
                agent_user_id,
                "restock_item.removed",
                f'Removed "{item_name}" from the restock list.',
            )
        return True


def delete_all_restock_items(
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> int:
    with SessionLocal.begin() as session:
        result = session.execute(delete(RestockItem).where(RestockItem.shop_id == shop_id))
        count = result.rowcount or 0
        if count and agent_user_id is not None:
            insert_agent_log(
                session,
                agent_user_id,
                "restock_list.cleared",
                f"Cleared {count} item(s) from the restock list.",
            )
        return count
