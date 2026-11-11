import pandas as pd

from src.visualization import (
    plot_monthly_expenses,
    plot_category_expenses,
    plot_budget_comparison
)


def sample_data():
    return pd.DataFrame({
        "date": [
            "01-09-26",
            "15-09-26",
            "01-10-26",
            "15-10-26",
            "01-11-26"
        ],
        "description": [
            "Grocery Store",
            "Uber",
            "Netflix",
            "Electricity Bill",
            "Restaurant"
        ],
        "amount": [1000, 300, 649, 1200, 800],
        "type": ["expense"] * 5
    })


def test_monthly_chart(tmp_path):
    df = sample_data()

    result = plot_monthly_expenses(df, tmp_path)

    assert result.exists()
    assert result.stat().st_size > 0


def test_category_chart(tmp_path):
    df = sample_data()

    result = plot_category_expenses(df, tmp_path)

    assert result.exists()
    assert result.stat().st_size > 0


def test_budget_chart(tmp_path):
    df = sample_data()

    budgets = {
        "Food": 3000,
        "Transportation": 1000,
        "Entertainment": 1000,
        "Utilities": 2000
    }

    result = plot_budget_comparison(
        df, budgets, tmp_path
    )

    assert result.exists()
    assert result.stat().st_size > 0