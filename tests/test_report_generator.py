import pandas as pd

from src.report_generator import generate_report


def test_generate_pdf_report(tmp_path):

    df = pd.DataFrame({
        "date": [
            "01-09-26",
            "15-09-26",
            "01-10-26",
            "15-10-26"
        ],
        "description": [
            "Grocery Store",
            "Uber",
            "Netflix",
            "Electricity Bill"
        ],
        "amount": [1000, 300, 649, 1200],
        "type": ["expense"] * 4
    })

    budgets = {
        "Food": 3000,
        "Transportation": 1000,
        "Entertainment": 1000,
        "Utilities": 2000
    }

    report_path = tmp_path / "financial_report.pdf"

    result = generate_report(
        df,
        output_path=report_path,
        budgets=budgets
    )

    assert result.exists()
    assert result.stat().st_size > 0

    with open(result, "rb") as pdf:
        assert pdf.read(4) == b"%PDF"