
import pandas as pd
import pytest

from src.data_loader import load_transactions, clean_transactions


def test_load_transactions():
    df = load_transactions("data/transactions.csv")

    assert len(df) == 15
    assert list(df.columns) == [
        "date", "description", "amount", "type"
    ]


def test_clean_transactions():
    data = pd.DataFrame({
        "date": ["2026-10-01", "invalid-date", "2026-10-03"],
        "description": ["Grocery", "Uber", "Netflix"],
        "amount": [1200, 300, None],
        "type": ["expense", "expense", "expense"]
    })

    cleaned = clean_transactions(data)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["description"] == "Grocery"


def test_clean_removes_duplicates():
    data = pd.DataFrame({
        "date": ["2026-10-01", "2026-10-01"],
        "description": ["Grocery", "Grocery"],
        "amount": [1200, 1200],
        "type": ["expense", "expense"]
    })

    cleaned = clean_transactions(data)

    assert len(cleaned) == 1


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load_transactions("data/nonexistent.csv")


def test_clean_removes_invalid_types():
    data = pd.DataFrame({
        "date": ["2026-10-01", "2026-10-02"],
        "description": ["Grocery", "Uber"],
        "amount": [1200, 300],
        "type": ["expense", "transfer"]
    })

    cleaned = clean_transactions(data)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["type"] == "expense"


def test_clean_does_not_modify_original():
    data = pd.DataFrame({
        "date": ["2026-10-01"],
        "description": ["Grocery"],
        "amount": [1200],
        "type": ["EXPENSE"]
    })

    original = data.copy(deep=True)

    clean_transactions(data)

    pd.testing.assert_frame_equal(data, original)

def test_clean_removes_empty_descriptions():
    data = pd.DataFrame({
        "date": ["2026-10-01", "2026-10-02"],
        "description": ["   ", "Uber"],
        "amount": [1200, 300],
        "type": ["expense", "expense"]
    })

    cleaned = clean_transactions(data)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["description"] == "Uber"