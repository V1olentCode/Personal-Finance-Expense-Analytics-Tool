
import pandas as pd
import math


def categorize_expenses(df):
    df = df.copy()

    categories = {
        "grocery": "Food",
        "restaurant": "Food",
        "uber": "Transportation",
        "taxi": "Transportation",
        "netflix": "Entertainment",
        "movie": "Entertainment",
        "electricity": "Utilities",
        "internet": "Utilities",
        "amazon": "Shopping"
    }

    def get_category(row):
        # Convert transaction type to lowercase and remove extra spaces for consistent comparison
        transaction_type = str(row["type"]).strip().lower()

        if transaction_type == "income":
            return "Income"

        description = str(row["description"]).strip().lower()

        for keyword, category in categories.items():
            if keyword in description:
                return category

        return "Other"

    df["category"] = df.apply(get_category, axis=1)

    return df


def calculate_total_expenses(df):
    if df.empty:
        return 0.0

    expenses = df[
        df["type"].astype(str).str.strip().str.lower() == "expense"
    ].copy()

    expenses["amount"] = pd.to_numeric(
        expenses["amount"], errors="coerce"
    )

    expenses = expenses[
    expenses["amount"].apply(
        lambda x: pd.notna(x) and math.isfinite(x)
    )
    ]

    return float(expenses["amount"].sum())


def calculate_monthly_expenses(df):
    if df.empty:
        return pd.Series(
            dtype="float64", index=pd.Index([], name="month"), name="amount"
        )

    expenses = df[
        df["type"].astype(str).str.strip().str.lower() == "expense"
    ].copy()

    expenses["date"] = pd.to_datetime(
        expenses["date"],
        format="%d-%m-%y",
        errors="coerce"
    )
    expenses["amount"] = pd.to_numeric(expenses["amount"], errors="coerce")

    # Remove rows with missing dates or non-finite amounts
    expenses = expenses.dropna(subset=["date", "amount"])
    
    expenses = expenses[
        expenses["amount"].apply(math.isfinite)
    ]

    expenses["month"] = expenses["date"].dt.strftime("%Y-%m")

    return expenses.groupby("month")["amount"].sum()


def calculate_category_expenses(df):
    if df.empty:
        return pd.Series(
            dtype="float64", index=pd.Index([], name="category"), name="amount"
        )

    if "category" not in df.columns:
        df = categorize_expenses(df)

    expenses = df[
        df["type"].astype(str).str.strip().str.lower() == "expense"
    ].copy()

    expenses["amount"] = pd.to_numeric(
    expenses["amount"], errors="coerce"
    )

    # Remove missing and infinite transaction amounts
    expenses = expenses.dropna(subset=["amount"])
    expenses = expenses[
        expenses["amount"].apply(math.isfinite)
    ]
    
    return expenses.groupby("category")["amount"].sum()



def calculate_total_income(df):
    income = df[
        df["type"].astype(str).str.strip().str.lower() == "income"
    ].copy()

    # No income transactions
    if income.empty:
        return 0.0

    income["amount"] = pd.to_numeric(
        income["amount"], errors="coerce"
    )

    # Remove missing and infinite income amounts
    income = income.dropna(subset=["amount"])

    income = income[
        income["amount"].apply(math.isfinite)
    ]

    return float(income["amount"].sum())
