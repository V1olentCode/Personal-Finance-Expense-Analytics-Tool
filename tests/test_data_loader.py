
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


def test_clean_missing_columns():
    data = pd.DataFrame({
        "date": ["2026-10-01"],
        "amount": [1200]
    })

    with pytest.raises(ValueError, match="Missing required columns"):
        clean_transactions(data)


def test_preserves_legitimate_identical_transactions():
    data = pd.DataFrame({
        "date": ["2026-10-01", "2026-10-01"],
        "description": ["Grocery Store", "Grocery Store"],
        "amount": [1200, 1200],
        "type": ["expense", "expense"]
    })

    cleaned = clean_transactions(data)

    assert len(cleaned) == 2


def test_clean_removes_non_finite_amounts():
    data = pd.DataFrame({
        "date": [
            "2026-10-01",
            "2026-10-02",
            "2026-10-03",
            "2026-10-04"
        ],
        "description": [
            "Grocery",
            "Uber",
            "Netflix",
            "Restaurant"
        ],
        "amount": [
            1200,
            float("inf"),
            float("-inf"),
            800
        ],
        "type": [
            "expense",
            "expense",
            "expense",
            "expense"
        ]
    })

    cleaned = clean_transactions(data)

    assert len(cleaned) == 2
    assert cleaned["amount"].tolist() == [1200, 800]


def test_clean_removes_invalid_calendar_dates():
    data = pd.DataFrame({
        "date": [
            "2026-10-01",
            "2026-02-30",
            "2026-13-01"
        ],
        "description": ["Grocery", "Uber", "Netflix"],
        "amount": [1200, 300, 649],
        "type": ["expense", "expense", "expense"]
    })

    cleaned = clean_transactions(data)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["description"] == "Grocery"


def test_clean_empty_dataframe():
    data = pd.DataFrame(
        columns=["date", "description", "amount", "type"]
    )

    cleaned = clean_transactions(data)

    assert cleaned.empty
    assert list(cleaned.columns) == [
        "date", "description", "amount", "type"
    ]

def test_clean_rejects_wrong_date_format():
    data = pd.DataFrame({
        "date": ["01/02/2026", "2026-10-01"],
        "description": ["Grocery", "Uber"],
        "amount": [1200, 300],
        "type": ["expense", "expense"]
    })

    cleaned = clean_transactions(data)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["description"] == "Uber"


def test_load_empty_csv(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")

    with pytest.raises(ValueError, match="CSV file is empty"):
        load_transactions(str(empty_file))


def test_load_malformed_csv(tmp_path):
    malformed_file = tmp_path / "malformed.csv"

    malformed_file.write_text(
        'date,description,amount,type\n'
        '2026-10-01,"Grocery,1200,expense\n'
    )

    with pytest.raises(ValueError, match="Invalid CSV format"):
        load_transactions(str(malformed_file))


def test_load_duplicate_columns(tmp_path):
    file = tmp_path / "duplicate.csv"

    file.write_text(
        "date,description,amount,amount,type\n"
        "2026-10-01,Grocery,1200,1500,expense\n"
    )

    with pytest.raises(ValueError, match="duplicate column names"):
        load_transactions(str(file))