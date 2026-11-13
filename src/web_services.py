"""Input validation and adapters between the web layer and legacy analytics."""

import math
import re

import pandas as pd
from werkzeug.utils import secure_filename

from src.analytics import (
    calculate_category_expenses,
    calculate_monthly_expenses,
    calculate_total_expenses,
    calculate_total_income,
    categorize_expenses,
)
from src.data_loader import clean_transactions, load_transactions
from src.database import TRANSACTION_COLUMNS

MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
ALLOWED_CATEGORIES = {
    "Food", "Transportation", "Entertainment", "Utilities", "Shopping", "Other"
}


def parse_upload(file_storage):
    filename = secure_filename(file_storage.filename or "")
    if not filename or not filename.lower().endswith(".csv"):
        raise ValueError("Upload a CSV file.")
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / filename
        file_storage.save(path)
        frame = clean_transactions(load_transactions(str(path)))
    if frame.empty:
        raise ValueError("CSV contains no valid transactions.")
    frame["date"] = pd.to_datetime(frame["date"], format="%Y-%m-%d")
    frame = categorize_expenses(frame)
    return frame


def valid_month(value):
    if value and MONTH_RE.fullmatch(value):
        return value
    return pd.Timestamp.today().strftime("%Y-%m")


def transaction_frame(frame):
    """Normalize a transaction frame to the schema required by legacy modules."""
    normalized = frame.copy()
    for column in TRANSACTION_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = pd.Series(index=normalized.index, dtype="object")
    # Keep the columns in a predictable order even if the input has extras.
    leading = [column for column in TRANSACTION_COLUMNS if column in normalized]
    trailing = [column for column in normalized if column not in leading]
    normalized = normalized[leading + trailing]
    return normalized


def report_frame(frame):
    """Adapt stored rows for the existing report and chart interfaces."""
    normalized = transaction_frame(frame)
    if "category" not in normalized.columns or normalized["category"].isna().all():
        normalized = categorize_expenses(normalized)
    if not normalized.empty:
        normalized["date"] = pd.to_datetime(normalized["date"]).dt.strftime("%d-%m-%y")
    return normalized


def summarize(frame):
    frame = transaction_frame(frame)
    if frame.empty:
        return {"income": 0.0, "expenses": 0.0, "balance": 0.0,
                "category_labels": [], "category_values": [],
                "month_labels": [], "month_values": []}
    # Legacy monthly analytics expects DD-MM-YY strings; adapt without changing it.
    analytics_frame = frame.copy()
    analytics_frame["date"] = pd.to_datetime(analytics_frame["date"]).dt.strftime("%d-%m-%y")
    category = calculate_category_expenses(analytics_frame)
    monthly = calculate_monthly_expenses(analytics_frame)
    income = calculate_total_income(analytics_frame)
    expenses = calculate_total_expenses(analytics_frame)
    return {"income": income, "expenses": expenses, "balance": income - expenses,
            "category_labels": [str(v) for v in category.index],
            "category_values": [float(v) for v in category.values],
            "month_labels": [str(v) for v in monthly.index],
            "month_values": [float(v) for v in monthly.values]}


def summarize_month(frame, month):
    """Summarize income, expenses, and expense charts for one calendar month."""
    frame = transaction_frame(frame)
    if frame.empty:
        selected = frame.copy()
    else:
        selected = frame[
            pd.to_datetime(frame["date"]).dt.strftime("%Y-%m") == month
        ].copy()

    empty = {
        "income": 0.0,
        "expenses": 0.0,
        "net_savings": 0.0,
        "category_labels": [],
        "category_values": [],
        "expense_trend_labels": [],
        "expense_trend_values": [],
    }
    if selected.empty:
        return empty

    selected["date"] = pd.to_datetime(selected["date"])
    selected = categorize_expenses(selected)
    expenses = selected[
        selected["type"].astype(str).str.strip().str.lower() == "expense"
    ].copy()
    income = calculate_total_income(selected)
    total_expenses = calculate_total_expenses(selected)
    categories = calculate_category_expenses(selected)
    if expenses.empty:
        trend_labels, trend_values = [], []
    else:
        daily = expenses.groupby(expenses["date"].dt.strftime("%d %b"))["amount"].sum()
        trend_labels = [str(label) for label in daily.index]
        trend_values = [float(value) for value in daily.values]

    return {
        "income": income,
        "expenses": total_expenses,
        "net_savings": income - total_expenses,
        "category_labels": [str(value) for value in categories.index],
        "category_values": [float(value) for value in categories.values],
        "expense_trend_labels": trend_labels,
        "expense_trend_values": trend_values,
    }


def monthly_budget_results(frame, budgets, month):
    frame = transaction_frame(frame)
    if frame.empty:
        selected = frame.copy()
    else:
        selected = frame[pd.to_datetime(frame["date"]).dt.strftime("%Y-%m") == month].copy()
    selected = report_frame(selected)
    # check_budget remains the authority for budget results and validation.
    from src.budget import check_budget
    return check_budget(selected, budgets)


def budget_amount(value):
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValueError("Enter a valid non-negative budget amount.")
    if not math.isfinite(amount) or amount < 0:
        raise ValueError("Enter a valid non-negative budget amount.")
    return amount
