import pandas as pd
from pathlib import Path

def main():
    # Initialize Path objects for csv files
    DATA_DIR = Path('data')
    OUTPUT_DIR = Path('output')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE_DEST = OUTPUT_DIR / 'transformed_transactions_monthly.csv'

    # Load data from files into dataframes
    customers_df = pd.read_csv((DATA_DIR / 'customers.csv'), dtype={"id": "Int64", "name": "string", "state": "string"})
    transactions_df = pd.read_csv((DATA_DIR / 'transactions.csv'), dtype={"transaction_id": "Int64", "customer_id": "Int64", "amount": "float"})

    # Rename for consistency
    customers_df = customers_df.rename(columns={'id': 'customer_id'})

    # Convert dates in both dataframes to datetime
    customers_df['signup_date'] = pd.to_datetime(customers_df['signup_date'], errors='coerce')
    transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'], errors='coerce')

    # Remove rows in customers with nulls in critical columns 
    customers_null_count = customers_df[['customer_id', 'name']].isnull().any(axis=1).sum()
    # Only need customer_id and name for the output
    customers_df = customers_df.dropna(subset=['customer_id', 'name'])
    print(f"Removed {customers_null_count} rows with null values from customers")

    # Remove rows in transactions with any nulls (all columns needed for output)
    transactions_null_count = transactions_df[['transaction_id', 'customer_id', 'amount', 'transaction_date']].isnull().any(axis=1).sum()
    transactions_df = transactions_df.dropna(subset=['transaction_id', 'customer_id', 'amount', 'transaction_date'])
    print(f"Removed {transactions_null_count} rows with null values from transactions")

    # Remove duplicate customers
    dup_cmr_count = customers_df.duplicated(subset=['customer_id']).sum()
    customers_df = customers_df.drop_duplicates(subset=['customer_id'], keep='first')
    print(f"Removed {dup_cmr_count} duplicate customers")

    # Remove duplicate transactions
    dup_txn_count = transactions_df.duplicated(subset=['transaction_id']).sum()
    transactions_df = transactions_df.drop_duplicates(subset=['transaction_id'], keep='first')
    print(f"Removed {dup_txn_count} duplicate transactions")

    # Remove orphaned transactions (referential integrity)
    valid_customer_ids = customers_df['customer_id'].unique()
    orphaned_count = (~transactions_df['customer_id'].isin(valid_customer_ids)).sum()
    transactions_df = transactions_df[transactions_df['customer_id'].isin(valid_customer_ids)]
    print(f"Removed {orphaned_count} orphaned transactions")

    # Left join customers and transactions
    joined_df = transactions_df.merge(customers_df[["customer_id", "name"]], on="customer_id", how="left")

    # Add year-month column
    joined_df["year_month"] = joined_df["transaction_date"].dt.strftime("%Y-%m")

    # Group and aggregate
    monthly_summary = (
        joined_df.groupby(["customer_id", "name", "year_month"], as_index=False)
        .agg(
            total_amount=("amount", "sum"),
            transaction_count=("transaction_id", "count"),
        )
    )

    # Round total_amount to 2 decimals
    monthly_summary["total_amount"] = monthly_summary["total_amount"].round(2)

    # Order final summary by customer_id and year-month
    monthly_summary = monthly_summary.sort_values(["customer_id", "year_month"])

    # Write final transformed csv
    monthly_summary.to_csv(OUTPUT_FILE_DEST, index=False)
    print(f"Wrote {len(monthly_summary)} rows to {OUTPUT_FILE_DEST}")

if __name__ == "__main__":
    main()