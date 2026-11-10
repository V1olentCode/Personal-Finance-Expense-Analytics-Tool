from src.data_loader import load_transactions, clean_transactions


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

    print("\nData loading and cleaning completed successfully!")


if __name__ == "__main__":
    main()