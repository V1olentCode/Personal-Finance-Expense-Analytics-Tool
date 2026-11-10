import csv
import pandas as pd
import numpy as np


def load_transactions(filepath: str) -> pd.DataFrame:
    """
    Load financial transactions from a CSV file.
    """

    try:
        # Read the original CSV headers
        with open(filepath, "r", newline="", encoding="utf-8") as file:
            headers = next(csv.reader(file))

        # Check for duplicate column names
        if len(headers) != len(set(headers)):
            raise ValueError("CSV contains duplicate column names.")

        # Load CSV into DataFrame
        df = pd.read_csv(filepath)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")

    except StopIteration:
        raise ValueError("The CSV file is empty.")

    except pd.errors.EmptyDataError:
        raise ValueError("The CSV file is empty.")

    except pd.errors.ParserError as error:
        raise ValueError(f"Invalid CSV format: {error}") from error

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

    required_columns = ["date", "description", "amount", "type"]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )
    
    # Convert date column to datetime
    df["date"] = pd.to_datetime(
        df["date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

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

    # Amount must be finite and positive
    df = df[np.isfinite(df["amount"])]
    df = df[df["amount"] > 0]

    # Reset DataFrame index
    df = df.reset_index(drop=True)

    return df
