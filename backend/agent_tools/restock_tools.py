"""Agent tools for the restocking list."""

from agents import RunContextWrapper, function_tool

from ..db_utils import restock_utils
from ._helpers import current_shop_id, json_result


@function_tool
def list_restock_items(context: RunContextWrapper[dict[str, int]], category_id: int | None = None) -> str:
    """List items on the restocking list, optionally limited to one category."""
    shop_id = current_shop_id(context)
    items = (restock_utils.get_all_restock_items(shop_id) if category_id is None
             else restock_utils.get_restock_items_by_category(category_id, shop_id))
    return json_result(items)


@function_tool
def add_restock_item(context: RunContextWrapper[dict[str, int]], name: str, category_id: int) -> str:
    """Add any item to the restock list; it does not need to exist in the catalog."""
    item_id = restock_utils.add_restock_item(name, category_id, current_shop_id(context))
    return json_result({"id": item_id, "name": name.strip(), "category_id": category_id})


@function_tool(needs_approval=True)
def remove_restock_item(context: RunContextWrapper[dict[str, int]], item_id: int) -> str:
    """Remove one restock entry after the user approves this action."""
    return json_result({"deleted": restock_utils.remove_restock_item(item_id, current_shop_id(context))})


@function_tool(needs_approval=True)
def clear_restock_list(context: RunContextWrapper[dict[str, int]]) -> str:
    """Clear the entire restock list after the user approves this action."""
    return json_result({"deleted_count": restock_utils.delete_all_restock_items(current_shop_id(context))})
