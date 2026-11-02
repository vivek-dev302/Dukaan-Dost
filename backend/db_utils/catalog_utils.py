"""Category and catalog item database operations."""

from typing import Any

from sqlalchemy import select

from ..database import SessionLocal
from ..models import Category, Item, RestockItem
from ._helpers import clean_text
from .agent_log_utils import insert_agent_log


def get_all_categories(shop_id: int) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Category.id, Category.name)
            .where(Category.shop_id == shop_id)
            .order_by(Category.name)
        ).mappings().all()
    return [dict(row) for row in rows]


def add_category(
    name: str,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> int:
    category_name = clean_text(name, "Category name")
    with SessionLocal.begin() as session:
        category = Category(name=category_name, shop_id=shop_id)
        session.add(category)
        session.flush()
        if agent_user_id is not None:
            insert_agent_log(session, agent_user_id, "category.added", f'Added category "{category_name}".')
        return category.id


def delete_category(
    category_id: int,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> bool:
    with SessionLocal.begin() as session:
        category = session.scalar(
            select(Category).where(Category.id == category_id, Category.shop_id == shop_id)
        )
        if category is None:
            return False
        if category.name.casefold() == "other":
            raise ValueError("The default Other category cannot be deleted")
        has_catalog_items = session.scalar(
            select(Item.id).where(Item.category_id == category_id, Item.shop_id == shop_id).limit(1)
        )
        has_restock_items = session.scalar(
            select(RestockItem.id).where(
                RestockItem.category_id == category_id, RestockItem.shop_id == shop_id
            ).limit(1)
        )
        if has_catalog_items or has_restock_items:
            raise ValueError("Remove this category's catalog and restock items first")
        category_name = category.name
        session.delete(category)
        if agent_user_id is not None:
            insert_agent_log(
                session, agent_user_id, "category.deleted", f'Deleted category "{category_name}".'
            )
        return True


def get_all_items(shop_id: int) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Item.id, Item.name, Item.category_id, Category.name.label("category_name"))
            .join(Category, (Category.id == Item.category_id) & (Category.shop_id == Item.shop_id))
            .where(Item.shop_id == shop_id)
            .order_by(Category.name, Item.name)
        ).mappings().all()
    return [dict(row) for row in rows]


def get_items_by_category(category_id: int, shop_id: int) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Item.id, Item.name, Item.category_id, Category.name.label("category_name"))
            .join(Category, (Category.id == Item.category_id) & (Category.shop_id == Item.shop_id))
            .where(Item.shop_id == shop_id, Item.category_id == category_id)
            .order_by(Item.name)
        ).mappings().all()
    return [dict(row) for row in rows]


def add_item(
    name: str,
    category_id: int,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> int:
    item_name = clean_text(name, "Item name")
    with SessionLocal.begin() as session:
        item = Item(name=item_name, category_id=category_id, shop_id=shop_id)
        session.add(item)
        session.flush()
        if agent_user_id is not None:
            category_name = session.scalar(
                select(Category.name).where(Category.id == category_id, Category.shop_id == shop_id)
            ) or str(category_id)
            insert_agent_log(
                session,
                agent_user_id,
                "catalog_item.added",
                f'Added catalog item "{item_name}" under "{category_name}".',
            )
        return item.id


def delete_item(
    item_id: int,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> bool:
    with SessionLocal.begin() as session:
        item = session.scalar(select(Item).where(Item.id == item_id, Item.shop_id == shop_id))
        if item is None:
            return False
        item_name = item.name
        session.delete(item)
        if agent_user_id is not None:
            insert_agent_log(
                session, agent_user_id, "catalog_item.deleted", f'Deleted catalog item "{item_name}".'
            )
        return True
