"""Khata credit record database operations."""
from datetime import date
from pathlib import Path
from typing import Any

from ..database import DEFAULT_DB_PATH, get_connection
from ._helpers import clean_text, ensure_customer


def add_credit_record(
    customer: str,
    amount_paise: int,
    description: str = "",
    entry_date: str | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    customer = clean_text(customer, "Customer name")
    if not isinstance(amount_paise, int) or amount_paise <= 0:
        raise ValueError("amount_paise must be a positive integer")
    entry_date = entry_date or date.today().isoformat()
    with get_connection(db_path) as connection:
        customer_id = ensure_customer(connection, customer)
        cursor = connection.execute(
            """INSERT INTO credit_records
               (customer_id, amount_paise, entry_date, description)
               VALUES (?, ?, ?, ?)""",
            (customer_id, amount_paise, entry_date, description.strip()),
        )
        connection.execute(
            "UPDATE customers SET total_paise = total_paise + ? WHERE id = ?",
            (amount_paise, customer_id),
        )
        return int(cursor.lastrowid)


def _credit_select(
    where: str = "", params: tuple = (), db_path: str | Path = DEFAULT_DB_PATH
) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """SELECT cr.id, c.id AS customer_id, c.name AS customer,
                      cr.amount_paise, cr.entry_date, cr.description
               FROM credit_records cr JOIN customers c ON c.id = cr.customer_id """
            + where
            + " ORDER BY cr.entry_date DESC, cr.id DESC",
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def get_all_credit_records(db_path: str | Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    return _credit_select(db_path=db_path)


def get_credit_records_by_date(
    entry_date: str, db_path: str | Path = DEFAULT_DB_PATH
) -> list[dict[str, Any]]:
    return _credit_select("WHERE cr.entry_date = ?", (entry_date,), db_path)


def get_credit_records_by_customer(
    customer: str, db_path: str | Path = DEFAULT_DB_PATH
) -> list[dict[str, Any]]:
    customer = clean_text(customer, "Customer name")
    return _credit_select("WHERE c.name = ? COLLATE NOCASE", (customer,), db_path)


def get_credit_records_by_customer_id(
    customer_id: int, db_path: str | Path = DEFAULT_DB_PATH
) -> list[dict[str, Any]]:
    return _credit_select("WHERE c.id = ?", (customer_id,), db_path)


def update_credit_record(
    record_id: int,
    *,
    customer: str | None = None,
    amount_paise: int | None = None,
    entry_date: str | None = None,
    description: str | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> bool:
    if amount_paise is not None and (
        not isinstance(amount_paise, int) or amount_paise <= 0
    ):
        raise ValueError("amount_paise must be a positive integer")
    if not any(v is not None for v in (customer, amount_paise, entry_date, description)):
        return False

    with get_connection(db_path) as connection:
        old = connection.execute(
            "SELECT customer_id, amount_paise FROM credit_records WHERE id = ?",
            (record_id,),
        ).fetchone()
        if old is None:
            return False

        old_customer_id = int(old["customer_id"])
        old_amount = int(old["amount_paise"])
        new_customer_id = old_customer_id
        fields: dict[str, Any] = {}
        if customer is not None:
            new_customer_id = ensure_customer(
                connection, clean_text(customer, "Customer name")
            )
            fields["customer_id"] = new_customer_id
        if amount_paise is not None:
            fields["amount_paise"] = amount_paise
        if entry_date is not None:
            fields["entry_date"] = entry_date
        if description is not None:
            fields["description"] = description.strip()

        assignments = ", ".join(f"{column} = ?" for column in fields)
        connection.execute(
            f"UPDATE credit_records SET {assignments} WHERE id = ?",
            [*fields.values(), record_id],
        )
        new_amount = amount_paise if amount_paise is not None else old_amount
        if old_customer_id == new_customer_id:
            connection.execute(
                "UPDATE customers SET total_paise = total_paise + ? WHERE id = ?",
                (new_amount - old_amount, old_customer_id),
            )
        else:
            connection.execute(
                "UPDATE customers SET total_paise = total_paise - ? WHERE id = ?",
                (old_amount, old_customer_id),
            )
            connection.execute(
                "UPDATE customers SET total_paise = total_paise + ? WHERE id = ?",
                (new_amount, new_customer_id),
            )
        return True


def delete_credit_record(
    record_id: int, db_path: str | Path = DEFAULT_DB_PATH
) -> bool:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT customer_id, amount_paise FROM credit_records WHERE id = ?",
            (record_id,),
        ).fetchone()
        if row is None:
            return False
        connection.execute("DELETE FROM credit_records WHERE id = ?", (record_id,))
        connection.execute(
            "UPDATE customers SET total_paise = total_paise - ? WHERE id = ?",
            (row["amount_paise"], row["customer_id"]),
        )
        return True


def delete_customer_credit_records(
    customer: str, db_path: str | Path = DEFAULT_DB_PATH
) -> int:
    customer = clean_text(customer, "Customer name")
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT id FROM customers WHERE name = ? COLLATE NOCASE", (customer,)
        ).fetchone()
        if row is None:
            return 0
        cursor = connection.execute(
            "DELETE FROM credit_records WHERE customer_id = ?", (row["id"],)
        )
        connection.execute(
            "UPDATE customers SET total_paise = 0 WHERE id = ?", (row["id"],)
        )
        return cursor.rowcount
