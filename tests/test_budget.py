import pandas as pd

from src.budget import check_budget


def test_check_budget():
    df = pd.DataFrame({
        "date": ["2026-10-01", "2026-10-02", "2026-10-03"],
        "description": ["Grocery Store", "Uber", "Salary"],
        "amount": [1200, 300, 30000],
        "type": ["expense", "expense", "income"]
    })

    budgets = {
        "Food": 1000,
        "Transportation": 500
    }

    result = check_budget(df, budgets)

    assert result.loc[0, "actual_expense"] == 1200
    assert result.loc[0, "status"] == "Exceeded"
    assert result.loc[1, "actual_expense"] == 300
    assert result.loc[1, "status"] == "Within Budget"