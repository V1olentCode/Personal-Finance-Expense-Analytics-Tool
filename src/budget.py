
import pandas as pd
import math

RESULT_COLUMNS = [
    "category", "budget", "actual_expense", "remaining_budget", "status"
]


def check_budget(df, budgets):
    # Validate budget values before doing any transaction aggregation.
    validated_budgets = {}
    for category, budget in budgets.items():
        try:
            budget = float(budget)
        except (TypeError, ValueError):
            raise ValueError(
                f"Budget for '{category}' must be a finite non-negative number."
            )
        if not math.isfinite(budget) or budget < 0:
            raise ValueError(
                f"Budget for '{category}' must be a finite non-negative number."
            )
        validated_budgets[category] = budget

    df = df.copy()
    for column in ("date", "description", "amount", "type"):
        if column not in df.columns:
            df[column] = pd.Series(dtype="object")

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

    # Remove infinite transaction amounts
    expenses = expenses[
        expenses["amount"].apply(math.isfinite)
    ]

    if expenses.empty:
        actual_expenses = pd.Series(dtype="float64")
    else:
        actual_expenses = expenses.groupby("category")["amount"].sum()

    results = []

    for category, budget in validated_budgets.items():
        actual = float(actual_expenses.get(category, 0))
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

    return pd.DataFrame(results, columns=RESULT_COLUMNS)
