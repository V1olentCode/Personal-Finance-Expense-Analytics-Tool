
import pandas as pd


def check_budget(df, budgets):
    if "category" not in df.columns:
        from src.analytics import categorize_expenses
        df = categorize_expenses(df)

    expenses = df[
        df["type"].astype(str).str.strip().str.lower() == "expense"
    ].copy()

    expenses["amount"] = pd.to_numeric(
        expenses["amount"], errors="coerce"
    )

    expenses = expenses.dropna(subset=["amount"])

    actual_expenses = expenses.groupby("category")["amount"].sum()

    results = []

    for category, budget in budgets.items():
        actual = float(actual_expenses.get(category, 0))
        budget = float(budget)
        remaining = budget - actual

        if actual > budget:
            status = "Exceeded"
        else:
            status = "Within Budget"

        results.append({
            "category": category,
            "budget": budget,
            "actual_expense": actual,
            "remaining_budget": remaining,
            "status": status
        })

    return pd.DataFrame(results)
