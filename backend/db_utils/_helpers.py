"""Shared helpers for database utility modules."""

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..models import Customer


def clean_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must not be empty")
    return value.strip()


def ensure_customer(session: Session, name: str, shop_id: int) -> int:
    session.execute(
        insert(Customer)
        .values(name=name, shop_id=shop_id)
        .on_conflict_do_nothing()
    )
    customer_id = session.scalar(
        select(Customer.id).where(
            Customer.shop_id == shop_id,
            func.lower(Customer.name) == name.lower(),
        )
    )
    return int(customer_id)
