
from pathlib import Path
from datetime import datetime

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.image import imread

from src.analytics import (
    calculate_total_income,
    calculate_total_expenses,
    calculate_category_expenses
)

from src.budget import check_budget

from src.visualization import (
    plot_monthly_expenses,
    plot_category_expenses,
    plot_budget_comparison
)


def format_currency(value):
    """Format a number as Indian Rupees."""
    return f"Rs. {float(value):,.2f}"


def add_chart_page(pdf, image_path, title):
    """Add a saved chart image as a PDF page."""

    fig, ax = plt.subplots(figsize=(11, 8))

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.axis("off")

    if Path(image_path).exists():
        image = imread(str(image_path))
        ax.imshow(image)
    else:
        ax.text(
            0.5, 0.5,
            "Chart is unavailable",
            ha="center",
            va="center",
            transform=ax.transAxes
        )

    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def generate_report(df, output_path="output/financial_report.pdf",
                    budgets=None):

    if budgets is None:
        budgets = {
            "Food": 5000,
            "Transportation": 2000,
            "Entertainment": 1000,
            "Utilities": 2500,
            "Shopping": 3000,
            "Other": 2000
        }

    report_path = Path(output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Financial calculations
    total_income = calculate_total_income(df)
    total_expenses = calculate_total_expenses(df)
    balance = total_income - total_expenses

    category_expenses = calculate_category_expenses(df)
    budget_results = check_budget(df, budgets)

    # Generate charts
    monthly_chart = plot_monthly_expenses(
        df, report_path.parent
    )

    category_chart = plot_category_expenses(
        df, report_path.parent
    )

    budget_chart = plot_budget_comparison(
        df, budgets, report_path.parent
    )

    with PdfPages(report_path) as pdf:

        # ==================================
        # PAGE 1: FINANCIAL SUMMARY
        # ==================================

        fig = plt.figure(figsize=(11.69, 8.27))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")

        ax.text(
            0.5, 0.94,
            "PERSONAL FINANCE ANALYTICS REPORT",
            ha="center",
            fontsize=19,
            fontweight="bold"
        )

        ax.text(
            0.5, 0.885,
            f"Generated on: {datetime.now():%d-%m-%Y}",
            ha="center",
            fontsize=10
        )

        # Financial summary cards
        summary_items = [
            ("TOTAL INCOME", total_income),
            ("TOTAL EXPENSES", total_expenses),
            ("REMAINING BALANCE", balance)
        ]

        positions = [0.19, 0.50, 0.81]

        for position, (label, value) in zip(
            positions, summary_items
        ):
            ax.text(
                position, 0.76,
                f"{label}\n{format_currency(value)}",
                ha="center",
                va="center",
                fontsize=12,
                fontweight="bold",
                bbox={
                    "boxstyle": "round,pad=1.0",
                    "facecolor": "#EAF0F6",
                    "edgecolor": "#B8C7D9"
                }
            )

        # Category table heading
        ax.text(
            0.08, 0.57,
            "CATEGORY-WISE EXPENDITURE",
            fontsize=14,
            fontweight="bold"
        )

        if not category_expenses.empty:

            category_data = [
                [str(category), format_currency(amount)]
                for category, amount in category_expenses.items()
            ]

            table = ax.table(
                cellText=category_data,
                colLabels=["Category", "Total Expenditure"],
                cellLoc="center",
                colLoc="center",
                bbox=[0.08, 0.12, 0.84, 0.38]
            )

            table.auto_set_font_size(False)
            table.set_fontsize(11)

            for (row, col), cell in table.get_celld().items():
                if row == 0:
                    cell.set_text_props(weight="bold")

        else:
            ax.text(
                0.5, 0.38,
                "No expense data available",
                ha="center",
                fontsize=12
            )

        pdf.savefig(fig)
        plt.close(fig)

        # ==================================
        # PAGE 2: BUDGET ANALYSIS
        # ==================================

        fig = plt.figure(figsize=(11.69, 8.27))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")

        ax.text(
            0.5, 0.93,
            "BUDGET ANALYSIS",
            ha="center",
            fontsize=19,
            fontweight="bold"
        )

        ax.text(
            0.5, 0.87,
            "Comparison of allocated budget and actual expenditure",
            ha="center",
            fontsize=10
        )

        if not budget_results.empty:

            table_data = []

            for _, row in budget_results.iterrows():

                table_data.append([
                    row["category"],
                    format_currency(row["budget"]),
                    format_currency(row["actual_expense"]),
                    format_currency(row["remaining_budget"]),
                    row["status"]
                ])

            table = ax.table(
                cellText=table_data,
                colLabels=[
                    "Category",
                    "Budget",
                    "Actual Expense",
                    "Remaining",
                    "Status"
                ],
                cellLoc="center",
                colLoc="center",
                colWidths=[0.18, 0.19, 0.22, 0.21, 0.17],
                bbox=[0.04, 0.29, 0.92, 0.45]
            )

            table.auto_set_font_size(False)
            table.set_fontsize(9)

            for (row, col), cell in table.get_celld().items():
                if row == 0:
                    cell.set_text_props(weight="bold")

        else:
            ax.text(
                0.5, 0.5,
                "No budget information available",
                ha="center",
                fontsize=12
            )

        exceeded = budget_results[
            budget_results["status"] == "Exceeded"
        ]

        ax.text(
            0.08, 0.18,
            f"Categories exceeding budget: {len(exceeded)}",
            fontsize=12,
            fontweight="bold"
        )

        pdf.savefig(fig)
        plt.close(fig)

        # ==================================
        # PAGE 3: MONTHLY EXPENSES
        # ==================================

        add_chart_page(
            pdf,
            monthly_chart,
            "Monthly Expenditure Analysis"
        )

        # ==================================
        # PAGE 4: CATEGORY EXPENSES
        # ==================================

        add_chart_page(
            pdf,
            category_chart,
            "Category-wise Expense Distribution"
        )

        # ==================================
        # PAGE 5: BUDGET COMPARISON
        # ==================================

        add_chart_page(
            pdf,
            budget_chart,
            "Budget vs Actual Expenditure"
        )

    return report_path
