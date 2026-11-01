"""Agent tools for customer khata records."""

from agents import RunContextWrapper, function_tool

from ..db_utils import credit_utils
from ._helpers import amount_to_paise, current_shop_id, current_user_id, json_result


@function_tool
def list_credit_records(
    context: RunContextWrapper[dict[str, int]],
    customer_id: int | None = None,
    customer_name: str | None = None,
    entry_date: str | None = None,
) -> str:
    """List khata entries, optionally filtered by customer ID/name or ISO date (YYYY-MM-DD)."""
    shop_id = current_shop_id(context)
    if customer_id is not None:
        records = credit_utils.get_credit_records_by_customer_id(customer_id, shop_id)
    elif customer_name:
        records = credit_utils.get_credit_records_by_customer(customer_name, shop_id)
    elif entry_date:
        records = credit_utils.get_credit_records_by_date(entry_date, shop_id)
    else:
        records = credit_utils.get_all_credit_records(shop_id)
    if entry_date and (customer_id is not None or customer_name):
        records = [record for record in records if record["entry_date"] == entry_date]
    return json_result(records)


@function_tool(needs_approval=True)
def add_credit_record(
    context: RunContextWrapper[dict[str, int]],
    customer: str,
    amount_rupees: float,
    description: str = "",
    entry_date: str | None = None,
) -> str:
    """Add a khata entry in rupees; the user must approve before it is saved."""
    record_id = credit_utils.add_credit_record(
        customer,
        amount_to_paise(amount_rupees),
        current_shop_id(context),
        description,
        entry_date,
        agent_user_id=current_user_id(context),
    )
    return json_result({"id": record_id, "customer": customer, "amount_rupees": amount_rupees})


@function_tool(needs_approval=True)
def update_credit_record(
    context: RunContextWrapper[dict[str, int]],
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
        current_shop_id(context),
        customer=customer,
        amount_paise=amount_paise,
        entry_date=entry_date,
        description=description,
        agent_user_id=current_user_id(context),
    )
    return json_result({"updated": updated, "record_id": record_id})


@function_tool(needs_approval=True)
def delete_credit_record(context: RunContextWrapper[dict[str, int]], record_id: int) -> str:
    """Delete one khata entry after the user approves this action."""
    return json_result({"deleted": credit_utils.delete_credit_record(
        record_id, current_shop_id(context), agent_user_id=current_user_id(context)
    )})


@function_tool(needs_approval=True)
def clear_customer_credit_records(context: RunContextWrapper[dict[str, int]], customer_name: str) -> str:
    """Delete all khata entries for a customer after the user approves this action."""
    count = credit_utils.delete_customer_credit_records(
        customer_name, current_shop_id(context), agent_user_id=current_user_id(context)
    )
    return json_result({"deleted_count": count, "customer": customer_name})
