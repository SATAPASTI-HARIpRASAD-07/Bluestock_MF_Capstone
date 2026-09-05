from pathlib import Path
import pandas as pd
RAW_DIR = Path("data/raw")
csv_files = sorted(RAW_DIR.glob("*.csv"))
print("=" * 70)
print("BLUESTOCK MUTUAL FUND DATASET INSPECTION")
print("=" * 70)
print(f"\nTotal CSV files found: {len(csv_files)}")
for file in csv_files:
    print("\n" + "=" * 70)
    print(f"FILE: {file.name}")
    print("=" * 70)
    try:
        df = pd.read_csv(file)
        print(f"Rows    : {len(df):,}")
        print(f"Columns : {len(df.columns)}")
        print("\nColumn names:")
        for col in df.columns:
            print(f"  - {col}")
        print("\nData types:")
        print(df.dtypes.to_string())
        print("\nMissing values:")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) == 0:
            print("  No missing values")
        else:
            for col, count in missing.items():
                if (
                    file.name.endswith("04_monthly_sip_inflows.csv")
                    and col == "yoy_growth_pct"
                ):
                    print(f"  {col}: {count} → EXPECTED")
                    print(
                        "    Reason: First 12 months have "
                        "no previous-year data."
                    )
                else:
                    print(f"  {col}: {count} → REVIEW REQUIRED")
        print("\nFirst 3 rows:")
        print(df.head(3).to_string(index=False))
    except Exception as e:
        print(f"ERROR reading {file.name}: {e}")
print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)