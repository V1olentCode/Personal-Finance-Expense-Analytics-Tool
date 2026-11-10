import pandas as pd

from src.analytics import (
    categorize_expenses,
    calculate_total_expenses,
    calculate_monthly_expenses,
    calculate_category_expenses,
    calculate_total_income
)


def sample_data():
    return pd.DataFrame({
        "date": ["2026-10-01", "2026-10-02", "2026-10-03"],
        "description": ["Grocery Store", "Uber", "Salary"],
        "amount": [1200, 300, 30000],
        "type": ["expense", "expense", "income"]
    })


def test_categorize_expenses():
    df = categorize_expenses(sample_data())

    assert df["category"].tolist() == [
        "Food", "Transportation", "Income"
    ]


def test_calculate_total_expenses():
    assert calculate_total_expenses(sample_data()) == 1500.0


def test_calculate_monthly_expenses():
    result = calculate_monthly_expenses(sample_data())

    assert result["2026-10"] == 1500


def test_calculate_category_expenses():
    df = categorize_expenses(sample_data())
    result = calculate_category_expenses(df)

    assert result["Food"] == 1200
    assert result["Transportation"] == 300


def test_calculate_total_income():
    assert calculate_total_income(sample_data()) == 30000.0