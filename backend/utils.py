"""CRUD helpers for Dukaan Dost's catalog, restock list, and khata records."""

from datetime import date
from pathlib import Path
from typing import Any

from .database import DEFAULT_DB_PATH, get_connection


def _clean_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must not be empty")
    return value.strip()


def _ensure_customer(connection: Any, name: str) -> int:
    connection.execute(
        "INSERT INTO customers (name) VALUES (?) ON CONFLICT(name) DO NOTHING", (name,)
    )
    row = connection.execute(
        "SELECT id FROM customers WHERE name = ? COLLATE NOCASE", (name,)
    ).fetchone()
    return int(row["id"])


# Catalog: categories and the items the shop carries (no quantities).
def get_all_categories(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    return [dict(row) for row in rows]


def add_category(name: str, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    name = _clean_text(name, "Category name")
    with get_connection(db_path) as connection:
        cursor = connection.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        return int(cursor.lastrowid)


def delete_category(category_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    """Delete an empty category; refuse while catalog or restock items use it."""
    with get_connection(db_path) as connection:
        exists = connection.execute(
            "SELECT 1 FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        if exists is None:
            return False
        has_items = connection.execute(
            "SELECT 1 FROM items WHERE category_id = ? LIMIT 1", (category_id,)
        ).fetchone()
        has_restock = connection.execute(
            "SELECT 1 FROM restock_items WHERE category_id = ? LIMIT 1", (category_id,)
        ).fetchone()
        if has_items or has_restock:
            raise ValueError("Remove this category's catalog and restock items first")
        connection.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        return True


def get_all_items(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT i.id, i.name, i.category_id, c.name AS category_name
               FROM items i JOIN categories c ON c.id = i.category_id
               ORDER BY c.name, i.name"""
        ).fetchall()
    return [dict(row) for row in rows]


def get_items_by_category(category_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT i.id, i.name, i.category_id, c.name AS category_name
               FROM items i JOIN categories c ON c.id = i.category_id
               WHERE i.category_id = ? ORDER BY i.name""",
            (category_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_item(name: str, category_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    name = _clean_text(name, "Item name")
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO items (name, category_id) VALUES (?, ?)", (name, category_id)
        )
        return int(cursor.lastrowid)


def delete_item(item_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    """Delete one item from the all-items catalog."""
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM items WHERE id = ?", (item_id,))
        return cursor.rowcount > 0


# Restocking list.
def get_all_restock_items(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT r.id, r.name, r.category_id, c.name AS category_name
               FROM restock_items r JOIN categories c ON c.id = r.category_id
               ORDER BY c.name, r.name"""
        ).fetchall()
    return [dict(row) for row in rows]


def get_restock_items_by_category(category_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT r.id, r.name, r.category_id, c.name AS category_name
               FROM restock_items r JOIN categories c ON c.id = r.category_id
               WHERE r.category_id = ? ORDER BY r.name""",
            (category_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_restock_item(name: str, category_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    name = _clean_text(name, "Restock item name")
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO restock_items (name, category_id) VALUES (?, ?)", (name, category_id)
        )
        return int(cursor.lastrowid)


def remove_restock_item(item_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM restock_items WHERE id = ?", (item_id,))
        return cursor.rowcount > 0


def delete_all_restock_items(db_path: str | Path = DEFAULT_DB_PATH) -> int:
    """Empty the restock list and return the number of removed rows."""
    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM restock_items")
        return cursor.rowcount


# Khata records store a purchase total and short description. Customer.total is
# the sum of that customer's current credit records, kept in sync by these helpers.
def get_all_customers(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT id, name, total FROM customers ORDER BY name"
        ).fetchall()
    return [dict(row) for row in rows]


def add_customer(name: str, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    """Create a customer with total 0; credit entries also create customers automatically."""
    name = _clean_text(name, "Customer name")
    with get_connection(db_path) as connection:
        cursor = connection.execute("INSERT INTO customers (name) VALUES (?)", (name,))
        return int(cursor.lastrowid)


def add_credit_record(
    customer: str,
    amount: float,
    description: str = "",
    entry_date: str | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    customer = _clean_text(customer, "Customer name")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    entry_date = entry_date or date.today().isoformat()
    with get_connection(db_path) as connection:
        customer_id = _ensure_customer(connection, customer)
        cursor = connection.execute(
            """INSERT INTO credit_records (customer_id, amount, entry_date, description)
               VALUES (?, ?, ?, ?)""",
            (customer_id, amount, entry_date, description.strip()),
        )
        connection.execute(
            "UPDATE customers SET total = total + ? WHERE id = ?", (amount, customer_id)
        )
        return int(cursor.lastrowid)


def get_all_credit_records(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT cr.id, c.id AS customer_id, c.name AS customer, cr.amount,
                      cr.entry_date, cr.description
               FROM credit_records cr JOIN customers c ON c.id = cr.customer_id
               ORDER BY cr.entry_date DESC, cr.id DESC"""
        ).fetchall()
    return [dict(row) for row in rows]


def get_credit_records_by_date(entry_date: str, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT cr.id, c.id AS customer_id, c.name AS customer, cr.amount,
                      cr.entry_date, cr.description
               FROM credit_records cr JOIN customers c ON c.id = cr.customer_id
               WHERE cr.entry_date = ? ORDER BY cr.id DESC""",
            (entry_date,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_credit_records_by_customer(customer: str, db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    customer = _clean_text(customer, "Customer name")
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT cr.id, c.id AS customer_id, c.name AS customer, cr.amount,
                      cr.entry_date, cr.description
               FROM credit_records cr JOIN customers c ON c.id = cr.customer_id
               WHERE c.name = ? COLLATE NOCASE ORDER BY cr.entry_date DESC, cr.id DESC""",
            (customer,),
        ).fetchall()
    return [dict(row) for row in rows]


def update_credit_record(
    record_id: int,
    *,
    customer: str | None = None,
    amount: float | None = None,
    entry_date: str | None = None,
    description: str | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> bool:
    """Update supplied fields and adjust customer totals when amount/customer changes."""
    if amount is not None and amount <= 0:
        raise ValueError("Amount must be greater than zero")
    if not any(value is not None for value in (customer, amount, entry_date, description)):
        return False

    with get_connection(db_path) as connection:
        old = connection.execute(
            "SELECT customer_id, amount FROM credit_records WHERE id = ?", (record_id,)
        ).fetchone()
        if old is None:
            return False

        old_customer_id = int(old["customer_id"])
        old_amount = float(old["amount"])
        new_customer_id = old_customer_id
        updates: dict[str, Any] = {}
        if customer is not None:
            new_customer_id = _ensure_customer(
                connection, _clean_text(customer, "Customer name")
            )
            updates["customer_id"] = new_customer_id
        if amount is not None:
            updates["amount"] = amount
        if entry_date is not None:
            updates["entry_date"] = entry_date
        if description is not None:
            updates["description"] = description.strip()

        assignments = ", ".join(f"{column} = ?" for column in updates)
        connection.execute(
            f"UPDATE credit_records SET {assignments} WHERE id = ?",
            [*updates.values(), record_id],
        )
        new_amount = amount if amount is not None else old_amount
        if old_customer_id == new_customer_id:
            connection.execute(
                "UPDATE customers SET total = total + ? WHERE id = ?",
                (new_amount - old_amount, old_customer_id),
            )
        else:
            connection.execute(
                "UPDATE customers SET total = total - ? WHERE id = ?",
                (old_amount, old_customer_id),
            )
            connection.execute(
                "UPDATE customers SET total = total + ? WHERE id = ?",
                (new_amount, new_customer_id),
            )
        return True


def delete_credit_record(record_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT customer_id, amount FROM credit_records WHERE id = ?", (record_id,)
        ).fetchone()
        if row is None:
            return False
        connection.execute("DELETE FROM credit_records WHERE id = ?", (record_id,))
        connection.execute(
            "UPDATE customers SET total = total - ? WHERE id = ?",
            (row["amount"], row["customer_id"]),
        )
        return True


def delete_customer_credit_records(customer: str, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    customer = _clean_text(customer, "Customer name")
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT id, total FROM customers WHERE name = ? COLLATE NOCASE", (customer,)
        ).fetchone()
        if row is None:
            return 0
        cursor = connection.execute(
            "DELETE FROM credit_records WHERE customer_id = ?", (row["id"],)
        )
        connection.execute("UPDATE customers SET total = 0 WHERE id = ?", (row["id"],))
        return cursor.rowcount
