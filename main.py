from src.data_loader import load_transactions, clean_transactions

from src.analytics import (
    categorize_expenses,
    calculate_total_expenses,
    calculate_monthly_expenses,
    calculate_category_expenses,
    calculate_total_income
)

from src.budget import check_budget

from src.report_generator import generate_report



def main():
    # Step 1: Load transaction data
    filepath = "data/transactions.csv"
    df = load_transactions(filepath)

    print("Original transaction data:")
    print(df.head())

    # Step 2: Clean transaction data
    df = clean_transactions(df)

    print("\nCleaned transaction data:")
    print(df.head())

    # Step 3: Categorize expenses
    df = categorize_expenses(df)

    print("\nCategorized transaction data:")
    print(df.head())

    # Step 4: Calculate financial statistics
    total_expenses = calculate_total_expenses(df)
    monthly_expenses = calculate_monthly_expenses(df)
    category_expenses = calculate_category_expenses(df)
    total_income = calculate_total_income(df)

    print("\nFinancial Summary:")
    print(f"Total Income: {total_income}")
    print(f"Total Expenses: {total_expenses}")

    print("\nMonthly Expenses:")
    print(monthly_expenses)

    print("\nCategory-wise Expenses:")
    print(category_expenses)

    # Step 5: Check category budgets
    budgets = {
        "Food": 5000,
        "Transportation": 2000,
        "Entertainment": 1500,
        "Utilities": 3000,
        "Shopping": 2500,
        "Other": 1000
    }

    budget_results = check_budget(df, budgets)

    print("\nBudget Analysis:")
    print(budget_results)

    # Step 6: Generate visualizations and PDF report
    report_path = generate_report(df, budgets=budgets)

    print(f"\nFinancial report generated successfully: {report_path}")

    print("\nData processing, analytics and budget analysis completed successfully!")


if __name__ == "__main__":
    main()