"""Agent tools for customer records."""

from agents import function_tool

from ..db_utils import customer_utils
from ._helpers import json_result


@function_tool
def list_customers() -> str:
    """List customers and their khata totals in integer paise."""
    return json_result(customer_utils.get_all_customers())


@function_tool
def add_customer(name: str) -> str:
    """Add a customer with an initial khata total of zero."""
    customer_id = customer_utils.add_customer(name)
    return json_result({"id": customer_id, "name": name.strip(), "total_paise": 0})
