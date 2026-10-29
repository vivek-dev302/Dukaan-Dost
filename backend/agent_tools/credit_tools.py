"""Agent tools for customer khata records."""

from agents import function_tool

from ..db_utils import credit_utils
from ._helpers import amount_to_paise, json_result


@function_tool
def list_credit_records(
    customer_id: int | None = None,
    customer_name: str | None = None,
    entry_date: str | None = None,
) -> str:
    """List khata entries, optionally filtered by customer ID/name or ISO date (YYYY-MM-DD)."""
    if customer_id is not None:
        records = credit_utils.get_credit_records_by_customer_id(customer_id)
    elif customer_name:
        records = credit_utils.get_credit_records_by_customer(customer_name)
    elif entry_date:
        records = credit_utils.get_credit_records_by_date(entry_date)
    else:
        records = credit_utils.get_all_credit_records()
    if entry_date and (customer_id is not None or customer_name):
        records = [record for record in records if record["entry_date"] == entry_date]
    return json_result(records)


@function_tool(needs_approval=True)
def add_credit_record(
    customer: str,
    amount_rupees: float,
    description: str = "",
    entry_date: str | None = None,
) -> str:
    """Add a khata entry in rupees; the user must approve before it is saved."""
    record_id = credit_utils.add_credit_record(
        customer, amount_to_paise(amount_rupees), description, entry_date
    )
    return json_result({"id": record_id, "customer": customer, "amount_rupees": amount_rupees})


@function_tool(needs_approval=True)
def update_credit_record(
    record_id: int,
    customer: str | None = None,
    amount_rupees: float | None = None,
    entry_date: str | None = None,
    description: str | None = None,
) -> str:
    """Edit a khata entry, including a partial payment amount; approval is required."""
    amount_paise = amount_to_paise(amount_rupees) if amount_rupees is not None else None
    updated = credit_utils.update_credit_record(
        record_id,
        customer=customer,
        amount_paise=amount_paise,
        entry_date=entry_date,
        description=description,
    )
    return json_result({"updated": updated, "record_id": record_id})


@function_tool(needs_approval=True)
def delete_credit_record(record_id: int) -> str:
    """Delete one khata entry after the user approves this action."""
    return json_result({"deleted": credit_utils.delete_credit_record(record_id)})


@function_tool(needs_approval=True)
def clear_customer_credit_records(customer_name: str) -> str:
    """Delete all khata entries for a customer after the user approves this action."""
    count = credit_utils.delete_customer_credit_records(customer_name)
    return json_result({"deleted_count": count, "customer": customer_name})
