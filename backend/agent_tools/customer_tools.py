"""Agent tools for customer records."""

from agents import RunContextWrapper, function_tool

from ..db_utils import customer_utils
from ._helpers import current_shop_id, current_user_id, json_result


@function_tool
def list_customers(context: RunContextWrapper[dict[str, int]]) -> str:
    """List customers and their khata totals in integer paise."""
    return json_result(customer_utils.get_all_customers(current_shop_id(context)))


@function_tool
def add_customer(context: RunContextWrapper[dict[str, int]], name: str) -> str:
    """Add a customer with an initial khata total of zero."""
    customer_id = customer_utils.add_customer(
        name, current_shop_id(context), agent_user_id=current_user_id(context)
    )
    return json_result({"id": customer_id, "name": name.strip(), "total_paise": 0})
