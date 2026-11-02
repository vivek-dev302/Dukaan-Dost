"""Khata credit record database operations."""

from datetime import date
from typing import Any

from sqlalchemy import and_, delete, func, select

from ..database import SessionLocal
from ..models import CreditRecord, Customer
from ._helpers import clean_text, ensure_customer
from .agent_log_utils import insert_agent_log


def add_credit_record(
    customer: str,
    amount_paise: int,
    shop_id: int,
    description: str = "",
    entry_date: str | None = None,
    *,
    agent_user_id: int | None = None,
) -> int:
    customer = clean_text(customer, "Customer name")
    if not isinstance(amount_paise, int) or amount_paise <= 0:
        raise ValueError("amount_paise must be a positive integer")
    entry_date = entry_date or date.today().isoformat()
    with SessionLocal.begin() as session:
        customer_id = ensure_customer(session, customer, shop_id)
        customer_row = session.get(Customer, customer_id)
        customer_row.total_paise += amount_paise
        record = CreditRecord(
            customer_id=customer_id,
            amount_paise=amount_paise,
            entry_date=entry_date,
            description=description.strip(),
            shop_id=shop_id,
        )
        session.add(record)
        session.flush()
        if agent_user_id is not None:
            insert_agent_log(
                session,
                agent_user_id,
                "credit_record.added",
                f"Added credit entry #{record.id} for {customer}: ₹{amount_paise / 100:.2f}.",
            )
        return record.id


def _credit_select(shop_id: int, *filters: Any) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(
                CreditRecord.id,
                Customer.id.label("customer_id"),
                Customer.name.label("customer"),
                CreditRecord.amount_paise,
                CreditRecord.entry_date,
                CreditRecord.description,
            )
            .join(
                Customer,
                and_(
                    Customer.id == CreditRecord.customer_id,
                    Customer.shop_id == CreditRecord.shop_id,
                ),
            )
            .where(CreditRecord.shop_id == shop_id, *filters)
            .order_by(CreditRecord.entry_date.desc(), CreditRecord.id.desc())
        ).mappings().all()
    return [dict(row) for row in rows]


def get_all_credit_records(shop_id: int) -> list[dict[str, Any]]:
    return _credit_select(shop_id)


def get_credit_records_by_date(entry_date: str, shop_id: int) -> list[dict[str, Any]]:
    return _credit_select(shop_id, CreditRecord.entry_date == entry_date)


def get_credit_records_by_customer(customer: str, shop_id: int) -> list[dict[str, Any]]:
    customer = clean_text(customer, "Customer name")
    return _credit_select(
        shop_id, func.lower(Customer.name) == customer.lower()
    )


def get_credit_records_by_customer_id(customer_id: int, shop_id: int) -> list[dict[str, Any]]:
    return _credit_select(shop_id, Customer.id == customer_id)


def update_credit_record(
    record_id: int,
    shop_id: int,
    *,
    customer: str | None = None,
    amount_paise: int | None = None,
    entry_date: str | None = None,
    description: str | None = None,
    agent_user_id: int | None = None,
) -> bool:
    if amount_paise is not None and (not isinstance(amount_paise, int) or amount_paise <= 0):
        raise ValueError("amount_paise must be a positive integer")
    if not any(value is not None for value in (customer, amount_paise, entry_date, description)):
        return False

    with SessionLocal.begin() as session:
        record = session.scalar(
            select(CreditRecord).where(
                CreditRecord.id == record_id, CreditRecord.shop_id == shop_id
            )
        )
        if record is None:
            return False

        old_customer = session.get(Customer, record.customer_id)
        old_customer_id = record.customer_id
        old_amount = record.amount_paise
        new_customer_id = old_customer_id
        if customer is not None:
            new_customer_id = ensure_customer(
                session, clean_text(customer, "Customer name"), shop_id
            )
            record.customer_id = new_customer_id
        if amount_paise is not None:
            record.amount_paise = amount_paise
        if entry_date is not None:
            record.entry_date = entry_date
        if description is not None:
            record.description = description.strip()

        new_amount = record.amount_paise
        if old_customer_id == new_customer_id:
            old_customer.total_paise += new_amount - old_amount
        else:
            old_customer.total_paise -= old_amount
            new_customer = session.get(Customer, new_customer_id)
            new_customer.total_paise += new_amount

        if agent_user_id is not None:
            changed_fields = []
            if customer is not None:
                changed_fields.append(f"customer to {customer.strip()}")
            if amount_paise is not None:
                changed_fields.append(f"amount to ₹{amount_paise / 100:.2f}")
            if entry_date is not None:
                changed_fields.append(f"date to {entry_date}")
            if description is not None:
                changed_fields.append("description")
            insert_agent_log(
                session,
                agent_user_id,
                "credit_record.updated",
                f"Updated credit entry #{record_id} for {customer or old_customer.name} ({', '.join(changed_fields)}).",
            )
        return True


def delete_credit_record(
    record_id: int,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> bool:
    with SessionLocal.begin() as session:
        record = session.scalar(
            select(CreditRecord).where(
                CreditRecord.id == record_id, CreditRecord.shop_id == shop_id
            )
        )
        if record is None:
            return False
        customer = session.get(Customer, record.customer_id)
        amount_paise = record.amount_paise
        customer.total_paise -= amount_paise
        session.delete(record)
        if agent_user_id is not None:
            insert_agent_log(
                session,
                agent_user_id,
                "credit_record.deleted",
                f"Deleted credit entry #{record_id} for {customer.name}: ₹{amount_paise / 100:.2f}.",
            )
        return True


def delete_customer_credit_records(
    customer: str,
    shop_id: int,
    *,
    agent_user_id: int | None = None,
) -> int:
    customer_name = clean_text(customer, "Customer name")
    with SessionLocal.begin() as session:
        customer_row = session.scalar(
            select(Customer).where(
                Customer.shop_id == shop_id,
                func.lower(Customer.name) == customer_name.lower(),
            )
        )
        if customer_row is None:
            return 0
        count = session.scalar(
            select(func.count(CreditRecord.id)).where(
                CreditRecord.customer_id == customer_row.id,
                CreditRecord.shop_id == shop_id,
            )
        ) or 0
        session.execute(
            delete(CreditRecord).where(
                CreditRecord.customer_id == customer_row.id,
                CreditRecord.shop_id == shop_id,
            )
        )
        customer_row.total_paise = 0
        if count and agent_user_id is not None:
            insert_agent_log(
                session,
                agent_user_id,
                "credit_records.cleared",
                f"Deleted {count} credit entr{'y' if count == 1 else 'ies'} for {customer_row.name}.",
            )
        return count
