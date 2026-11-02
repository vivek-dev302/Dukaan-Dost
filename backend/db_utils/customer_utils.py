"""Customer database operations."""

from typing import Any

from sqlalchemy import select

from ..database import SessionLocal
from ..models import Customer
from ._helpers import clean_text
from .agent_log_utils import insert_agent_log


def get_all_customers(shop_id: int) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(Customer.id, Customer.name, Customer.total_paise)
            .where(Customer.shop_id == shop_id)
            .order_by(Customer.name)
        ).mappings().all()
    return [dict(row) for row in rows]


def add_customer(
    name: str,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> int:
    customer_name = clean_text(name, "Customer name")
    with SessionLocal.begin() as session:
        customer = Customer(name=customer_name, shop_id=shop_id)
        session.add(customer)
        session.flush()
        if agent_user_id is not None:
            insert_agent_log(
                session, agent_user_id, "customer.added", f'Added customer "{customer_name}".'
            )
        return customer.id
