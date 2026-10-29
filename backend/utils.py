"""CRUD helpers for the Dukaan Dost MVP."""
from datetime import date
from pathlib import Path
from typing import Any
from .database import DEFAULT_DB_PATH, get_connection


def _clean_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must not be empty")
    return value.strip()


def _ensure_customer(connection: Any, name: str) -> int:
    connection.execute("INSERT INTO customers (name) VALUES (?) ON CONFLICT(name) DO NOTHING", (name,))
    row = connection.execute("SELECT id FROM customers WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
    return int(row["id"])

# Catalog
def get_all_categories(db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        rows = c.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    return [dict(r) for r in rows]

def add_category(name, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        cur = c.execute("INSERT INTO categories (name) VALUES (?)", (_clean_text(name, "Category name"),))
        return int(cur.lastrowid)

def delete_category(category_id, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        category = c.execute("SELECT name FROM categories WHERE id=?", (category_id,)).fetchone()
        if category is None:
            return False
        if category["name"].casefold() == "other":
            raise ValueError("The default Other category cannot be deleted")
        if (c.execute("SELECT 1 FROM items WHERE category_id=? LIMIT 1", (category_id,)).fetchone()
                or c.execute("SELECT 1 FROM restock_items WHERE category_id=? LIMIT 1", (category_id,)).fetchone()):
            raise ValueError("Remove this category's catalog and restock items first")
        c.execute("DELETE FROM categories WHERE id=?", (category_id,))
        return True

def get_all_items(db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        rows = c.execute("SELECT i.id,i.name,i.category_id,c.name AS category_name FROM items i JOIN categories c ON c.id=i.category_id ORDER BY c.name,i.name").fetchall()
    return [dict(r) for r in rows]

def get_items_by_category(category_id, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        rows = c.execute("SELECT i.id,i.name,i.category_id,c.name AS category_name FROM items i JOIN categories c ON c.id=i.category_id WHERE i.category_id=? ORDER BY i.name", (category_id,)).fetchall()
    return [dict(r) for r in rows]

def add_item(name, category_id, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        cur = c.execute("INSERT INTO items (name,category_id) VALUES (?,?)", (_clean_text(name, "Item name"), category_id))
        return int(cur.lastrowid)

def delete_item(item_id, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        return c.execute("DELETE FROM items WHERE id=?", (item_id,)).rowcount > 0

# Restock list
def get_all_restock_items(db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        rows = c.execute("SELECT r.id,r.name,r.category_id,c.name AS category_name FROM restock_items r JOIN categories c ON c.id=r.category_id ORDER BY c.name,r.name").fetchall()
    return [dict(r) for r in rows]

def get_restock_items_by_category(category_id, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        rows = c.execute("SELECT r.id,r.name,r.category_id,c.name AS category_name FROM restock_items r JOIN categories c ON c.id=r.category_id WHERE r.category_id=? ORDER BY r.name", (category_id,)).fetchall()
    return [dict(r) for r in rows]

def add_restock_item(name, category_id, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        cur = c.execute("INSERT INTO restock_items (name,category_id) VALUES (?,?)", (_clean_text(name, "Restock item name"), category_id))
        return int(cur.lastrowid)

def remove_restock_item(item_id, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        return c.execute("DELETE FROM restock_items WHERE id=?", (item_id,)).rowcount > 0

def delete_all_restock_items(db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        return c.execute("DELETE FROM restock_items").rowcount

# Customer totals are integer paise and equal the sum of current khata entries.
def get_all_customers(db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        rows = c.execute("SELECT id,name,total_paise FROM customers ORDER BY name").fetchall()
    return [dict(r) for r in rows]

def add_customer(name, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        cur = c.execute("INSERT INTO customers (name) VALUES (?)", (_clean_text(name, "Customer name"),))
        return int(cur.lastrowid)

def add_credit_record(customer, amount_paise, description="", entry_date=None, db_path=DEFAULT_DB_PATH):
    customer = _clean_text(customer, "Customer name")
    if not isinstance(amount_paise, int) or amount_paise <= 0:
        raise ValueError("amount_paise must be a positive integer")
    entry_date = entry_date or date.today().isoformat()
    with get_connection(db_path) as c:
        customer_id = _ensure_customer(c, customer)
        cur = c.execute("INSERT INTO credit_records(customer_id,amount_paise,entry_date,description) VALUES (?,?,?,?)", (customer_id, amount_paise, entry_date, description.strip()))
        c.execute("UPDATE customers SET total_paise=total_paise+? WHERE id=?", (amount_paise, customer_id))
        return int(cur.lastrowid)

def _credit_select(where="", params=(), db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        rows = c.execute("SELECT cr.id,c.id AS customer_id,c.name AS customer,cr.amount_paise,cr.entry_date,cr.description FROM credit_records cr JOIN customers c ON c.id=cr.customer_id " + where + " ORDER BY cr.entry_date DESC,cr.id DESC", params).fetchall()
    return [dict(r) for r in rows]

def get_all_credit_records(db_path=DEFAULT_DB_PATH):
    return _credit_select(db_path=db_path)

def get_credit_records_by_date(entry_date, db_path=DEFAULT_DB_PATH):
    return _credit_select("WHERE cr.entry_date=?", (entry_date,), db_path)

def get_credit_records_by_customer(customer, db_path=DEFAULT_DB_PATH):
    return _credit_select("WHERE c.name=? COLLATE NOCASE", (_clean_text(customer, "Customer name"),), db_path)

def get_credit_records_by_customer_id(customer_id, db_path=DEFAULT_DB_PATH):
    return _credit_select("WHERE c.id=?", (customer_id,), db_path)

def update_credit_record(record_id, *, customer=None, amount_paise=None, entry_date=None, description=None, db_path=DEFAULT_DB_PATH):
    if amount_paise is not None and (not isinstance(amount_paise, int) or amount_paise <= 0):
        raise ValueError("amount_paise must be a positive integer")
    if not any(v is not None for v in (customer, amount_paise, entry_date, description)):
        return False
    with get_connection(db_path) as c:
        old = c.execute("SELECT customer_id,amount_paise FROM credit_records WHERE id=?", (record_id,)).fetchone()
        if old is None:
            return False
        old_id, old_amount = int(old["customer_id"]), int(old["amount_paise"])
        new_id = old_id
        fields = {}
        if customer is not None:
            new_id = _ensure_customer(c, _clean_text(customer, "Customer name"))
            fields["customer_id"] = new_id
        if amount_paise is not None: fields["amount_paise"] = amount_paise
        if entry_date is not None: fields["entry_date"] = entry_date
        if description is not None: fields["description"] = description.strip()
        c.execute("UPDATE credit_records SET " + ",".join(f"{k}=?" for k in fields) + " WHERE id=?", [*fields.values(), record_id])
        new_amount = amount_paise if amount_paise is not None else old_amount
        if old_id == new_id:
            c.execute("UPDATE customers SET total_paise=total_paise+? WHERE id=?", (new_amount-old_amount, old_id))
        else:
            c.execute("UPDATE customers SET total_paise=total_paise-? WHERE id=?", (old_amount, old_id))
            c.execute("UPDATE customers SET total_paise=total_paise+? WHERE id=?", (new_amount, new_id))
        return True

def delete_credit_record(record_id, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        row = c.execute("SELECT customer_id,amount_paise FROM credit_records WHERE id=?", (record_id,)).fetchone()
        if row is None: return False
        c.execute("DELETE FROM credit_records WHERE id=?", (record_id,))
        c.execute("UPDATE customers SET total_paise=total_paise-? WHERE id=?", (row["amount_paise"], row["customer_id"]))
        return True

def delete_customer_credit_records(customer, db_path=DEFAULT_DB_PATH):
    with get_connection(db_path) as c:
        row = c.execute("SELECT id FROM customers WHERE name=? COLLATE NOCASE", (_clean_text(customer, "Customer name"),)).fetchone()
        if row is None: return 0
        count = c.execute("DELETE FROM credit_records WHERE customer_id=?", (row["id"],)).rowcount
        c.execute("UPDATE customers SET total_paise=0 WHERE id=?", (row["id"],))
        return count

