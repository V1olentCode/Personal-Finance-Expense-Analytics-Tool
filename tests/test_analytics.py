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
        "date": ["01-10-26", "02-10-26", "03-10-26"],
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


def test_calculate_total_expenses_ignores_non_finite_amounts():
    df = pd.DataFrame({
        "date": [
            "2026-10-01",
            "2026-10-02",
            "2026-10-03",
            "2026-10-04"
        ],
        "description": [
            "Grocery Store",
            "Uber",
            "Restaurant",
            "Netflix"
        ],
        "amount": [100, float("inf"), float("-inf"), float("nan")],
        "type": ["expense", "expense", "expense", "expense"]
    })

    assert calculate_total_expenses(df) == 100.0


def test_calculate_monthly_expenses_ignores_non_finite_amounts():
    df = pd.DataFrame({
        "date": [
        "01-10-26",
        "02-10-26",
        "03-10-26"
        ],
        "description": ["Grocery", "Uber", "Restaurant"],
        "amount": [100, float("inf"), float("nan")],
        "type": ["expense", "expense", "expense"]
    })

    result = calculate_monthly_expenses(df)

    assert result["2026-10"] == 100


def test_calculate_category_expenses_ignores_non_finite_amounts():
    df = pd.DataFrame({
        "date": ["2026-10-01", "2026-10-02", "2026-10-03"],
        "description": ["Grocery Store", "Uber", "Restaurant"],
        "amount": [100, float("inf"), float("nan")],
        "type": ["expense", "expense", "expense"]
    })

    df = categorize_expenses(df)
    result = calculate_category_expenses(df)

    assert result["Food"] == 100


def test_calculate_total_income_ignores_non_finite_amounts():
    df = pd.DataFrame({
        "description": ["Salary", "Freelance", "Bonus"],
        "amount": [1000, float("inf"), float("nan")],
        "type": ["income", "income", "income"]
    })

    result = calculate_total_income(df)

    assert result == 1000.0