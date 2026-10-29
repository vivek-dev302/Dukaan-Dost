"""Agent tools for the optional item catalog and categories."""

from agents import function_tool

from ..db_utils import catalog_utils
from ._helpers import json_result


@function_tool
def list_categories() -> str:
    """List all product categories."""
    return json_result(catalog_utils.get_all_categories())


@function_tool
def list_catalog_items(category_id: int | None = None) -> str:
    """List catalog items, optionally limited to one category."""
    items = (catalog_utils.get_all_items() if category_id is None
             else catalog_utils.get_items_by_category(category_id))
    return json_result(items)


@function_tool
def add_category(name: str) -> str:
    """Add a category. The default Other category already exists."""
    category_id = catalog_utils.add_category(name)
    return json_result({"id": category_id, "name": name.strip()})


@function_tool(needs_approval=True)
def delete_category(category_id: int) -> str:
    """Delete an empty category after the user approves this action."""
    return json_result({"deleted": catalog_utils.delete_category(category_id)})


@function_tool
def add_catalog_item(name: str, category_id: int) -> str:
    """Add an item to the optional all-items catalog."""
    item_id = catalog_utils.add_item(name, category_id)
    return json_result({"id": item_id, "name": name.strip(), "category_id": category_id})


@function_tool(needs_approval=True)
def delete_catalog_item(item_id: int) -> str:
    """Delete an item from the catalog after the user approves this action."""
    return json_result({"deleted": catalog_utils.delete_item(item_id)})
