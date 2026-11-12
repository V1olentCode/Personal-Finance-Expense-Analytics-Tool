"""SQLite persistence for web application transactions and monthly budgets."""

import sqlite3
from pathlib import Path

import pandas as pd

TRANSACTION_COLUMNS = ["date", "description", "amount", "type", "category"]


def empty_transactions(*, include_id=False):
    """Return an empty transaction frame with the same schema as stored rows."""
    columns = (["id"] if include_id else []) + TRANSACTION_COLUMNS
    return pd.DataFrame(columns=columns)


def connect(database_path):
    if str(database_path) != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path):
    with connect(database_path) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                UNIQUE(month, category)
            );
        """)


def add_transactions(database_path, frame):
    records = []
    for _, row in frame.iterrows():
        date = pd.to_datetime(row["date"]).strftime("%Y-%m-%d")
        records.append((date, str(row["description"]), float(row["amount"]),
                        str(row["type"]), str(row["category"])))
    with connect(database_path) as db:
        db.executemany(
            "INSERT INTO transactions(date, description, amount, type, category) VALUES (?, ?, ?, ?, ?)",
            records,
        )
    return len(records)


def get_transactions(database_path, *, month=None, kind=None, category=None,
                     search=None, start_date=None, end_date=None):
    clauses, params = [], []
    if month:
        clauses.append("substr(date, 1, 7) = ?")
        params.append(month)
    if kind in {"income", "expense"}:
        clauses.append("type = ?")
        params.append(kind)
    if category:
        clauses.append("category = ?")
        params.append(category)
    if search:
        clauses.append("description LIKE ?")
        params.append(f"%{search}%")
    if start_date:
        clauses.append("date >= ?")
        params.append(start_date)
    if end_date:
        clauses.append("date <= ?")
        params.append(end_date)
    query = "SELECT id, date, description, amount, type, category FROM transactions"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY date DESC, id DESC"
    with connect(database_path) as db:
        rows = db.execute(query, params).fetchall()
    return pd.DataFrame([dict(row) for row in rows], columns=["id"] + TRANSACTION_COLUMNS)


def save_budget(database_path, month, category, amount):
    with connect(database_path) as db:
        db.execute("""INSERT INTO budgets(month, category, amount) VALUES (?, ?, ?)
            ON CONFLICT(month, category) DO UPDATE SET amount = excluded.amount""",
                   (month, category, amount))


def get_budgets(database_path, month):
    with connect(database_path) as db:
        rows = db.execute(
            "SELECT category, amount FROM budgets WHERE month = ? ORDER BY category",
            (month,),
        ).fetchall()
    return {row["category"]: float(row["amount"]) for row in rows}
