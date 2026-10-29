"""SQLite database setup for Dukaan Dost."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "dukaandost.db"
SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE
);
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    UNIQUE (name, category_id)
);
CREATE TABLE IF NOT EXISTS restock_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    UNIQUE (name, category_id)
);
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
    total_paise INTEGER NOT NULL DEFAULT 0 CHECK (total_paise >= 0)
);
CREATE TABLE IF NOT EXISTS credit_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    amount_paise INTEGER NOT NULL CHECK (amount_paise > 0),
    entry_date TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category_id);
CREATE INDEX IF NOT EXISTS idx_restock_category ON restock_items(category_id);
CREATE INDEX IF NOT EXISTS idx_credit_customer_date ON credit_records(customer_id, entry_date);
"""

def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.executescript(SCHEMA)

@contextmanager
def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> Iterator[sqlite3.Connection]:
    init_db(db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
