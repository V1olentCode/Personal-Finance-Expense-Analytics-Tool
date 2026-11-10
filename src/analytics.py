
import pandas as pd


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
    expenses = df[
        df["type"].astype(str).str.strip().str.lower() == "expense"
    ]

    return float(pd.to_numeric(expenses["amount"], errors="coerce").sum())


def calculate_monthly_expenses(df):
    expenses = df[
        df["type"].astype(str).str.strip().str.lower() == "expense"
    ].copy()

    expenses["date"] = pd.to_datetime(expenses["date"], errors="coerce")
    expenses["amount"] = pd.to_numeric(expenses["amount"], errors="coerce")

    expenses = expenses.dropna(subset=["date", "amount"])

    expenses["month"] = expenses["date"].dt.strftime("%Y-%m")

    return expenses.groupby("month")["amount"].sum()


def calculate_category_expenses(df):
    if "category" not in df.columns:
        df = categorize_expenses(df)

    expenses = df[
        df["type"].astype(str).str.strip().str.lower() == "expense"
    ].copy()

    expenses["amount"] = pd.to_numeric(expenses["amount"], errors="coerce")
    expenses = expenses.dropna(subset=["amount"])

    return expenses.groupby("category")["amount"].sum()


def calculate_total_income(df):
    income = df[
        df["type"].astype(str).str.strip().str.lower() == "income"
    ]

    return float(pd.to_numeric(income["amount"], errors="coerce").sum())
