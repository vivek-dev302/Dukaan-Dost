"""Function tools available to the Dukaan Dost agent."""

from .catalog_tools import (
    add_catalog_item,
    add_category,
    delete_catalog_item,
    delete_category,
    list_catalog_items,
    list_categories,
)
from .credit_tools import (
    add_credit_record,
    clear_customer_credit_records,
    delete_credit_record,
    list_credit_records,
    update_credit_record,
)
from .customer_tools import add_customer, list_customers
from .restock_tools import (
    add_restock_item,
    clear_restock_list,
    list_restock_items,
    remove_restock_item,
)

TOOLS = [
    list_categories,
    list_catalog_items,
    list_restock_items,
    list_customers,
    list_credit_records,
    add_category,
    delete_category,
    add_catalog_item,
    delete_catalog_item,
    add_restock_item,
    remove_restock_item,
    clear_restock_list,
    add_customer,
    add_credit_record,
    update_credit_record,
    delete_credit_record,
    clear_customer_credit_records,
]

__all__ = ["TOOLS"]
