
from pathlib import Path

import numpy as np
import matplotlib

# Use a non-interactive backend for saving charts
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


def plot_monthly_expenses(df, output_dir="output"):
    """
    Generate a bar chart showing monthly expenses.
    """

    # Import Member 2's analytics function
    from src.analytics import calculate_monthly_expenses

    # Calculate monthly expenses
    monthly_expenses = calculate_monthly_expenses(df)

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create the chart
    fig, ax = plt.subplots(figsize=(10, 6))

    if monthly_expenses.empty:
        ax.text(
            0.5, 0.5,
            "No expense data available",
            ha="center",
            va="center",
            transform=ax.transAxes
        )
        ax.set_axis_off()

    else:
        months = monthly_expenses.index.astype(str)
        amounts = monthly_expenses.values

        # Create bar chart
        bars = ax.bar(months, amounts)

        # Add titles and labels
        ax.set_title("Monthly Expenditure Analysis")
        ax.set_xlabel("Month")
        ax.set_ylabel("Expenses (INR)")

        # Format Y-axis as currency
        ax.yaxis.set_major_formatter(
            StrMethodFormatter("₹{x:,.0f}")
        )

        # Display values above bars
        ax.bar_label(
            bars,
            labels=[f"₹{value:,.0f}" for value in amounts],
            padding=3
        )

        ax.tick_params(axis="x", rotation=30)

        ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    # Save the chart
    file_path = output_path / "monthly_expenses.png"
    fig.savefig(file_path, dpi=150, bbox_inches="tight")

    plt.close(fig)

    return file_path


def plot_category_expenses(df, output_dir="output"):
    """
    Generate a pie chart showing category-wise expenses.
    """

    from src.analytics import calculate_category_expenses

    # Calculate expenditure for each category
    category_expenses = calculate_category_expenses(df)

    # Remove invalid and zero/negative values
    category_expenses = category_expenses[
        np.isfinite(category_expenses) & (category_expenses > 0)
    ]

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create the chart
    fig, ax = plt.subplots(figsize=(8, 8))

    if category_expenses.empty:
        ax.text(
            0.5, 0.5,
            "No expense data available",
            ha="center",
            va="center",
            transform=ax.transAxes
        )
        ax.set_axis_off()

    else:
        # Generate pie chart
        ax.pie(
            category_expenses.values,
            labels=category_expenses.index,
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white"}
        )

        ax.set_title("Category-wise Expense Distribution")
        ax.axis("equal")

    fig.tight_layout()

    # Save the chart
    file_path = output_path / "category_expenses.png"
    fig.savefig(file_path, dpi=150, bbox_inches="tight")

    plt.close(fig)

    return file_path


def plot_budget_comparison(df, budgets, output_dir="output"):
    """
    Generate a bar chart comparing budget with actual expenses.
    """

    from src.budget import check_budget

    # Calculate budget comparison
    budget_results = check_budget(df, budgets)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create chart
    fig, ax = plt.subplots(figsize=(11, 6))

    if budget_results.empty:
        ax.text(
            0.5, 0.5,
            "No budget data available",
            ha="center",
            va="center",
            transform=ax.transAxes
        )
        ax.set_axis_off()

    else:
        categories = budget_results["category"].astype(str).tolist()

        budget_values = budget_results["budget"].to_numpy(dtype=float)
        actual_values = budget_results["actual_expense"].to_numpy(dtype=float)

        # Set positions for the bars
        x = np.arange(len(categories))
        width = 0.35

        # Create two sets of bars
        budget_bars = ax.bar(
            x - width / 2,
            budget_values,
            width,
            label="Allocated Budget"
        )

        actual_bars = ax.bar(
            x + width / 2,
            actual_values,
            width,
            label="Actual Expenses"
        )

        # Add chart labels
        ax.set_title("Budget vs Actual Expenditure")
        ax.set_xlabel("Expense Categories")
        ax.set_ylabel("Amount (INR)")

        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=25, ha="right")

        ax.yaxis.set_major_formatter(
            StrMethodFormatter("₹{x:,.0f}")
        )

        # Display values above bars
        ax.bar_label(
            budget_bars,
            labels=[f"₹{v:,.0f}" for v in budget_values],
            padding=3,
            fontsize=8
        )

        ax.bar_label(
            actual_bars,
            labels=[f"₹{v:,.0f}" for v in actual_values],
            padding=3,
            fontsize=8
        )

        ax.legend()
        ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    # Save chart
    file_path = output_path / "budget_comparison.png"

    fig.savefig(file_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return file_path
