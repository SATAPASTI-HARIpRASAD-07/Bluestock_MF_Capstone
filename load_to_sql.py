from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
PROCESSED_DIR = Path("data/processed")
DATABASE_FILE = Path("bluestock_mf.db")
engine = create_engine(
    f"sqlite:///{DATABASE_FILE}",
    echo=False
)
TABLE_MAP = {
    "01_fund_master.csv": "fund_master",
    "02_nav_history.csv": "nav_history",
    "03_aum_by_fund_house.csv": "aum_by_fund_house",
    "04_monthly_sip_inflows.csv": "monthly_sip_inflows",
    "05_category_inflows.csv": "category_inflows",
    "06_industry_folio_count.csv": "industry_folio_count",
    "07_scheme_performance.csv": "scheme_performance",
    "08_investor_transactions.csv": "investor_transactions",
    "09_portfolio_holdings.csv": "portfolio_holdings",
    "10_benchmark_indices.csv": "benchmark_indices",
}
print("=" * 70)
print("BLUESTOCK MUTUAL FUND → SQL DATABASE LOADING")
print("=" * 70)
loaded_tables = 0
for filename, table_name in TABLE_MAP.items():
    file_path = PROCESSED_DIR / filename
    print(f"\nLoading: {filename}")
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        continue
    try:
        df = pd.read_csv(file_path)
        # Convert date columns to proper date format
        date_columns = [
            "date",
            "transaction_date",
            "portfolio_date",
            "launch_date",
            "month",
        ]
        for column in date_columns:
            if column in df.columns:
                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )
        # Write dataframe to SQLite
        df.to_sql(
            table_name,
            con=engine,
            if_exists="replace",
            index=False
        )
        print(f"  ✓ Table created : {table_name}")
        print(f"  ✓ Rows          : {len(df):,}")
        print(f"  ✓ Columns       : {len(df.columns)}")
        loaded_tables += 1
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
print("\n" + "=" * 70)
print("DATABASE VERIFICATION")
print("=" * 70)
with engine.connect() as connection:
    result = connection.execute(
        text(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' ORDER BY name"
        )
    )
    tables = [row[0] for row in result]
    for table in tables:
        result = connection.execute(
            text(f'SELECT COUNT(*) FROM "{table}"')
        )
        row_count = result.scalar()
        print(f"  ✓ {table:<30} {row_count:,} rows")
print("\n" + "=" * 70)
print("SQL DATABASE LOADING COMPLETE")
print("=" * 70)
print(f"\nTables successfully loaded: {loaded_tables}")
print(f"Database file: {DATABASE_FILE}")