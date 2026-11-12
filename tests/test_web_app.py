import io

import pandas as pd
import pytest

from src.web_app import create_app
from src import database
from src.budget import check_budget
from src.web_services import monthly_budget_results, report_frame, transaction_frame


@pytest.fixture
def app(tmp_path):
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-key",
        "DATABASE": str(tmp_path / "test.sqlite3"),
        "MAX_CONTENT_LENGTH": 1024,
    })
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


def csv_bytes(rows="2026-10-01,Grocery Store,1200,expense\n"):
    return ("date,description,amount,type\n" + rows).encode()


def upload(client, rows="2026-10-01,Grocery Store,1200,expense\n"):
    return client.post("/transactions", data={
        "file": (io.BytesIO(csv_bytes(rows)), "transactions.csv"),
        "month": "2026-10",
    }, content_type="multipart/form-data", follow_redirects=True)


def test_dashboard_loads_empty_dataset(client):
    response = client.get("/?month=2026-10")
    assert response.status_code == 200
    assert b"Good to see you" in response.data
    assert "Monthly Overview — October 2026".encode("utf-8") in response.data
    assert b"Monthly income" in response.data
    assert b"Monthly expenses" in response.data
    assert b"Monthly net savings" in response.data
    assert b"No expense data for October 2026" in response.data
    assert b"No transactions in October 2026" in response.data
    assert b"monthlyChart" in response.data
    assert b"monthlyTrendChart" in response.data


def test_dashboard_month_switch_only_changes_monthly_sections(client):
    upload(client, "2026-10-01,Grocery Store,1200,expense\n2026-10-02,Uber,300,expense\n2026-10-03,Salary,30000,income\n2026-11-01,Uber,300,expense\n2026-11-02,Grocery Store,200,expense\n2026-11-03,Freelance Work,5000,income\n")
    client.post("/budgets?month=2026-10", data={
        "category": "Food", "amount": "2000"
    })
    client.post("/budgets?month=2026-11", data={
        "category": "Transportation", "amount": "500"
    })

    october = client.get("/?month=2026-10").data
    november = client.get("/?month=2026-11").data

    # The all-time summary and charts stay fixed as the selected month changes.
    assert b"All-time spending trend" in october and b"All-time spending trend" in november
    assert b"All-time expense breakdown" in october and b"All-time expense breakdown" in november
    assert b"data-values='[1500.0, 500.0]'" in october
    assert b"data-values='[1500.0, 500.0]'" in november
    assert b"data-values='[1400.0, 600.0]'" in october
    assert b"data-values='[1400.0, 600.0]'" in november
    assert "₹35000.00".encode("utf-8") in october
    assert "₹35000.00".encode("utf-8") in november
    assert "₹2000.00".encode("utf-8") in october
    assert "₹2000.00".encode("utf-8") in november
    assert "₹33000.00".encode("utf-8") in october
    assert "₹33000.00".encode("utf-8") in november

    # Selected-month summaries and charts use only that month's transactions.
    october_text = october.decode("utf-8")
    november_text = november.decode("utf-8")
    assert "Monthly Overview — October 2026" in october_text
    assert "Monthly income" in october_text
    assert "₹30000.00" in october_text
    assert "Monthly expenses" in october_text
    assert "₹1500.00" in october_text
    assert "Monthly net savings" in october_text
    assert "₹28500.00" in october_text
    assert "data-values='[1200.0, 300.0]'" in october_text
    assert "Monthly Overview — November 2026" in november_text
    assert "₹5000.00" in november_text
    assert "₹500.00" in november_text
    assert "₹4500.00" in november_text
    assert "data-values='[300.0, 200.0]'" in november_text

    # Budgets and recent transactions remain scoped to the selected month.
    assert "Budget progress for October 2026" in october_text
    assert "Latest activity in October 2026" in october_text
    assert "Grocery Store" in october_text and "Freelance Work" not in october_text
    assert "Budget progress for November 2026" in november_text
    assert "Latest activity in November 2026" in november_text
    assert "Freelance Work" in november_text and "Salary" not in november_text


def test_monthly_summary_empty_month_uses_zero_values_and_empty_charts():
    from src.web_services import summarize_month

    summary = summarize_month(pd.DataFrame(), "2026-10")
    assert summary == {
        "income": 0.0,
        "expenses": 0.0,
        "net_savings": 0.0,
        "category_labels": [],
        "category_values": [],
        "expense_trend_labels": [],
        "expense_trend_values": [],
    }


def test_empty_web_transaction_frame_has_legacy_columns():
    frame = transaction_frame(pd.DataFrame())
    assert {"date", "description", "amount", "type", "category"}.issubset(frame.columns)


def test_check_budget_empty_result_keeps_documented_columns():
    result = check_budget(pd.DataFrame(), {})
    assert result.empty
    assert result.columns.tolist() == [
        "category", "budget", "actual_expense", "remaining_budget", "status"
    ]


@pytest.mark.parametrize("budgets", [{}, {"Food": 500}])
def test_check_budget_empty_transactions_have_stable_result_schema(budgets):
    result = check_budget(pd.DataFrame(), budgets)
    assert result.columns.tolist() == [
        "category", "budget", "actual_expense", "remaining_budget", "status"
    ]
    if budgets:
        assert result.to_dict("records") == [{
            "category": "Food", "budget": 500.0, "actual_expense": 0.0,
            "remaining_budget": 500.0, "status": "Within Budget"
        }]


def test_monthly_budget_result_handles_empty_transactions_and_budgets():
    result = monthly_budget_results(pd.DataFrame(), {}, "2026-10")
    assert result.empty
    assert result.columns.tolist() == [
        "category", "budget", "actual_expense", "remaining_budget", "status"
    ]


def test_report_frame_has_all_required_columns_for_empty_data():
    frame = report_frame(pd.DataFrame())
    assert frame.columns.tolist() == ["date", "description", "amount", "type", "category"]
    assert frame.empty


def test_report_frame_preserves_populated_data_and_category():
    source = pd.DataFrame({
        "date": ["2026-10-01"], "description": ["Grocery"],
        "amount": [25.0], "type": ["expense"], "category": ["Food"]
    })
    frame = report_frame(source)
    assert frame.columns.tolist() == ["date", "description", "amount", "type", "category"]
    assert frame.iloc[0].to_dict() == {
        "date": "01-10-26", "description": "Grocery", "amount": 25.0,
        "type": "expense", "category": "Food"
    }


def test_csv_upload_and_sqlite_persistence(client, app):
    response = upload(client)
    assert response.status_code == 200
    assert b"Imported 1 transactions" in response.data
    frame = database.get_transactions(app.config["DATABASE"])
    assert len(frame) == 1
    assert frame.iloc[0]["date"] == "2026-10-01"
    assert frame.iloc[0]["category"] == "Food"


@pytest.mark.parametrize("body", [
    b"", b"date,description,amount\n2026-10-01,Tea,2\n",
    b"date,description,amount,type\n2026-10-01,Tea,nope,expense\n",
    b"date,description,amount,type\n2026-02-30,Tea,2,expense\n",
])
def test_invalid_csv_rejected(client, body):
    response = client.post("/transactions", data={
        "file": (io.BytesIO(body), "bad.csv")
    }, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"error" in response.data.lower()
    assert b"No transactions found" in response.data


def test_upload_rejects_non_csv(client):
    response = client.post("/transactions", data={
        "file": (io.BytesIO(b"hello"), "transactions.txt")
    }, content_type="multipart/form-data")
    assert b"Upload a CSV file" in response.data


def test_upload_enforces_size_limit(client):
    body = b"date,description,amount,type\n" + b"x" * 2048
    response = client.post("/transactions", data={
        "file": (io.BytesIO(body), "large.csv")
    }, content_type="multipart/form-data")
    assert response.status_code == 413


def test_transaction_filtering(client):
    upload(client, "2026-10-01,Grocery Store,1200,expense\n2026-10-02,Salary,5000,income\n2026-11-01,Uber,300,expense\n")
    response = client.get("/transactions?month=2026-10&type=expense&search=Grocery")
    assert response.status_code == 200
    assert b"Grocery Store" in response.data
    assert b"Salary" not in response.data
    assert b"Uber" not in response.data


def test_monthly_budget_creation_update_and_scoped_actuals(client, app):
    upload(client, "2026-10-01,Grocery Store,1200,expense\n2026-11-01,Grocery Store,800,expense\n")
    response = client.post("/budgets?month=2026-10", data={
        "month": "2026-10", "category": "Food", "amount": "2000"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Monthly budget saved" in response.data
    assert "Spent ₹1200.00".encode("utf-8") in response.data
    client.post("/budgets?month=2026-10", data={
        "month": "2026-10", "category": "Food", "amount": "1000"
    }, follow_redirects=True)
    assert database.get_budgets(app.config["DATABASE"], "2026-10") == {"Food": 1000.0}
    assert database.get_budgets(app.config["DATABASE"], "2026-11") == {}
    result = client.get("/budgets?month=2026-10")
    assert "Spent ₹1200.00".encode("utf-8") in result.data
    assert b"Exceeded" in result.data


def test_budget_rejects_invalid_category_and_amount(client):
    response = client.post("/budgets?month=2026-10", data={
        "category": "Income", "amount": "-1"
    })
    assert b"Choose a valid expense category" in response.data
    assert database.get_budgets(client.application.config["DATABASE"], "2026-10") == {}


@pytest.mark.parametrize("category,amount,message", [
    ("Income", "100", b"Choose a valid expense category"),
    ("Food", "-1", b"valid non-negative budget amount"),
    ("Food", "nan", b"valid non-negative budget amount"),
])
def test_invalid_budgets_are_rejected_without_server_error(client, category, amount, message):
    response = client.post("/budgets?month=2026-10", data={
        "category": category, "amount": amount
    })
    assert response.status_code == 200
    assert message in response.data
    assert database.get_budgets(client.application.config["DATABASE"], "2026-10") == {}


@pytest.mark.parametrize("category,amount,message", [
    ("Income", "-1", b"Choose a valid expense category"),
    ("Food", "nan", b"valid non-negative budget amount"),
])
def test_budget_validation_precedes_empty_transaction_aggregation(client, category, amount, message):
    response = client.post("/budgets?month=2026-10", data={
        "category": category, "amount": amount
    })
    assert response.status_code == 200
    assert message in response.data


def test_pdf_download_for_empty_dataset(client):
    response = client.get("/reports/monthly.pdf?month=2026-10")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")


def test_empty_pdf_route_passes_schema_complete_frame_to_report_generator(
    client, monkeypatch
):
    from src import web_routes

    captured = {}

    def fake_generate_report(frame, output_path, budgets=None):
        captured["frame"] = frame.copy()
        output_path.write_bytes(b"%PDF-test")
        return output_path

    monkeypatch.setattr(web_routes, "generate_report", fake_generate_report)
    response = client.get("/reports/monthly.pdf?month=2026-10")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")
    assert captured["frame"].columns.tolist() == [
        "date", "description", "amount", "type", "category"
    ]
    assert captured["frame"].empty


def test_pdf_download_with_persisted_data(client):
    upload(client)
    response = client.get("/reports/monthly.pdf?month=2026-10")
    assert response.status_code == 200
    assert response.data.startswith(b"%PDF")


def test_invalid_month_rejected(client):
    assert client.get("/budgets?month=2026-13").status_code == 400

