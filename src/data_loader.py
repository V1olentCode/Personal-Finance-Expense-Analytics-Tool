
import pandas as pd


def load_transactions(filepath: str) -> pd.DataFrame:
    """
    Load financial transactions from a CSV file.
    """

    try:
        df = pd.read_csv(filepath)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")

    required_columns = ["date", "description", "amount", "type"]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate transaction data.
    """

    df = df.copy()

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Convert amount column to numeric
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Remove extra spaces
    df["description"] = df["description"].astype("string").str.strip()

    # Standardize transaction types
    df["type"] = df["type"].astype("string").str.lower().str.strip()

    # Treat empty descriptions and types as missing
    df["description"] = df["description"].replace("", pd.NA)
    df["type"] = df["type"].replace("", pd.NA)

    # Remove rows with missing required values
    df = df.dropna(
        subset=["date", "description", "amount", "type"]
    )

    # Keep only valid transaction types
    df = df[df["type"].isin(["income", "expense"])]

    # Amount must be positive
    df = df[df["amount"] > 0]

    # Remove duplicate transactions
    df = df.drop_duplicates()

    # Reset DataFrame index
    df = df.reset_index(drop=True)

    return df
