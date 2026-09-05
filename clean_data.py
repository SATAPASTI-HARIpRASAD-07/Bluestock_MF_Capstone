from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# BLUESTOCK MUTUAL FUND ANALYTICS
# DAY 2 - DATA CLEANING
# ============================================================

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# Find files using their dataset number
# ------------------------------------------------------------

def find_file(number):
    matches = list(RAW_DIR.glob(f"*{number}_*.csv"))

    if not matches:
        raise FileNotFoundError(
            f"Could not find dataset number {number} in {RAW_DIR}"
        )

    if len(matches) > 1:
        print(f"WARNING: Multiple files found for dataset {number}")

    return matches[0]


# ------------------------------------------------------------
# General cleaning
# ------------------------------------------------------------

def clean_text_columns(df):
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    return df


def remove_duplicates(df, name):
    before = len(df)

    df = df.drop_duplicates().copy()

    removed = before - len(df)

    print(f"{name}: removed {removed:,} duplicate rows")

    return df


# ============================================================
# 01 - FUND MASTER
# ============================================================

def clean_fund_master():

    file = find_file("01")
    df = pd.read_csv(file)

    df = clean_text_columns(df)
    df = remove_duplicates(df, "01_fund_master")

    # Date
    df["launch_date"] = pd.to_datetime(
        df["launch_date"],
        errors="coerce"
    )

    # Numeric columns
    numeric_columns = [
        "expense_ratio_pct",
        "exit_load_pct",
        "min_sip_amount",
        "min_lumpsum_amount"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Validate primary key
    duplicate_codes = df["amfi_code"].duplicated().sum()

    if duplicate_codes:
        print(
            f"WARNING: {duplicate_codes} duplicate AMFI codes "
            f"in fund master"
        )

    output = PROCESSED_DIR / "01_fund_master.csv"

    df.to_csv(output, index=False)

    print(f"01_fund_master → {len(df):,} rows")

    return df


# ============================================================
# 02 - NAV HISTORY
# ============================================================

def clean_nav_history():

    file = find_file("02")
    df = pd.read_csv(file)

    df = clean_text_columns(df)

    # Parse date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Numeric NAV
    df["nav"] = pd.to_numeric(
        df["nav"],
        errors="coerce"
    )

    # Sort as required
    df = df.sort_values(
        ["amfi_code", "date"]
    ).reset_index(drop=True)

    # Remove duplicates
    before = len(df)

    df = df.drop_duplicates(
        subset=["amfi_code", "date"],
        keep="last"
    )

    print(
        f"02_nav_history: removed "
        f"{before - len(df):,} duplicate date/fund rows"
    )

    # Forward-fill missing NAV values within each fund.
    # This handles missing NAV values that occur on
    # holiday/weekend records without creating artificial
    # dates that were not present in the source dataset.
    missing_before = df["nav"].isna().sum()

    df["nav"] = (
        df.groupby("amfi_code")["nav"]
        .ffill()
    )

    missing_after = df["nav"].isna().sum()

    print(
        f"02_nav_history: missing NAV before fill = "
        f"{missing_before:,}"
    )

    print(
        f"02_nav_history: missing NAV after fill = "
        f"{missing_after:,}"
    )

    # Validate NAV > 0
    invalid_nav = (df["nav"] <= 0).sum()

    if invalid_nav:
        print(
            f"WARNING: {invalid_nav:,} NAV values are <= 0"
        )
    else:
        print("02_nav_history: all NAV values > 0")

    # Validate dates
    invalid_dates = df["date"].isna().sum()

    if invalid_dates:
        print(
            f"WARNING: {invalid_dates:,} invalid NAV dates"
        )

    output = PROCESSED_DIR / "02_nav_history.csv"

    df.to_csv(output, index=False)

    print(f"02_nav_history → {len(df):,} rows")

    return df


# ============================================================
# 03 - AUM BY FUND HOUSE
# ============================================================

def clean_aum_by_fund_house():

    file = find_file("03")
    df = pd.read_csv(file)

    df = clean_text_columns(df)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    numeric_columns = [
        "aum_lakh_crore",
        "aum_crore",
        "num_schemes"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = remove_duplicates(
        df,
        "03_aum_by_fund_house"
    )

    output = PROCESSED_DIR / "03_aum_by_fund_house.csv"

    df.to_csv(output, index=False)

    print(f"03_aum_by_fund_house → {len(df):,} rows")

    return df


# ============================================================
# 04 - MONTHLY SIP INFLOWS
# ============================================================

def clean_monthly_sip():

    file = find_file("04")
    df = pd.read_csv(file)

    df = clean_text_columns(df)

    # Convert YYYY-MM into a proper date
    df["month"] = pd.to_datetime(
        df["month"],
        format="%Y-%m",
        errors="coerce"
    )

    numeric_columns = [
        "sip_inflow_crore",
        "active_sip_accounts_crore",
        "new_sip_accounts_lakh",
        "sip_aum_lakh_crore",
        "yoy_growth_pct"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # The source contains missing YoY values for early months.
    # These are retained because YoY cannot be calculated until
    # the previous year's corresponding month exists.
    print(
        "04_monthly_sip_inflows: missing yoy_growth_pct =",
        df["yoy_growth_pct"].isna().sum()
    )

    df = remove_duplicates(
        df,
        "04_monthly_sip_inflows"
    )

    output = PROCESSED_DIR / "04_monthly_sip_inflows.csv"

    df.to_csv(output, index=False)

    print(f"04_monthly_sip_inflows → {len(df):,} rows")

    return df


# ============================================================
# 05 - CATEGORY INFLOWS
# ============================================================

def clean_category_inflows():

    file = find_file("05")
    df = pd.read_csv(file)

    df = clean_text_columns(df)

    df["month"] = pd.to_datetime(
        df["month"],
        format="%Y-%m",
        errors="coerce"
    )

    df["net_inflow_crore"] = pd.to_numeric(
        df["net_inflow_crore"],
        errors="coerce"
    )

    df = remove_duplicates(
        df,
        "05_category_inflows"
    )

    output = PROCESSED_DIR / "05_category_inflows.csv"

    df.to_csv(output, index=False)

    print(f"05_category_inflows → {len(df):,} rows")

    return df


# ============================================================
# 06 - INDUSTRY FOLIO COUNT
# ============================================================

def clean_industry_folio():

    file = find_file("06")
    df = pd.read_csv(file)

    df = clean_text_columns(df)

    df["month"] = pd.to_datetime(
        df["month"],
        format="%Y-%m",
        errors="coerce"
    )

    numeric_columns = [
        "total_folios_crore",
        "equity_folios_crore",
        "debt_folios_crore",
        "hybrid_folios_crore",
        "others_folios_crore"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = remove_duplicates(
        df,
        "06_industry_folio_count"
    )

    output = PROCESSED_DIR / "06_industry_folio_count.csv"

    df.to_csv(output, index=False)

    print(f"06_industry_folio_count → {len(df):,} rows")

    return df


# ============================================================
# 07 - SCHEME PERFORMANCE
# ============================================================

def clean_scheme_performance():

    file = find_file("07")
    df = pd.read_csv(file)

    df = clean_text_columns(df)

    numeric_columns = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Flag rows where return values could not be converted
    return_columns = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct"
    ]

    df["return_anomaly_flag"] = (
        df[return_columns]
        .isna()
        .any(axis=1)
    )

    # Expense ratio requirement:
    # valid range = 0.1% to 2.5%
    df["expense_ratio_anomaly_flag"] = ~df[
        "expense_ratio_pct"
    ].between(0.1, 2.5, inclusive="both")

    # Overall anomaly flag
    df["anomaly_flag"] = (
        df["return_anomaly_flag"]
        | df["expense_ratio_anomaly_flag"]
    )

    df = remove_duplicates(
        df,
        "07_scheme_performance"
    )

    print(
        "07_scheme_performance: return anomalies =",
        df["return_anomaly_flag"].sum()
    )

    print(
        "07_scheme_performance: expense ratio anomalies =",
        df["expense_ratio_anomaly_flag"].sum()
    )

    output = PROCESSED_DIR / "07_scheme_performance.csv"

    df.to_csv(output, index=False)

    print(f"07_scheme_performance → {len(df):,} rows")

    return df


# ============================================================
# 08 - INVESTOR TRANSACTIONS
# ============================================================

def clean_investor_transactions():

    file = find_file("08")
    df = pd.read_csv(file)

    df = clean_text_columns(df)

    # Date
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    # Amount
    df["amount_inr"] = pd.to_numeric(
        df["amount_inr"],
        errors="coerce"
    )

    # Standardise transaction type
    transaction_map = {
        "sip": "SIP",
        "SIP": "SIP",
        "lumpsum": "Lumpsum",
        "Lumpsum": "Lumpsum",
        "lump sum": "Lumpsum",
        "Lump Sum": "Lumpsum",
        "redemption": "Redemption",
        "Redemption": "Redemption"
    }

    df["transaction_type"] = (
        df["transaction_type"]
        .astype(str)
        .str.strip()
        .map(transaction_map)
        .fillna(df["transaction_type"])
    )

    # Validate transaction types
    valid_transaction_types = {
        "SIP",
        "Lumpsum",
        "Redemption"
    }

    invalid_types = ~df[
        "transaction_type"
    ].isin(valid_transaction_types)

    print(
        "08_investor_transactions: invalid transaction types =",
        invalid_types.sum()
    )

    # Validate amount > 0
    invalid_amount = (
        df["amount_inr"].isna()
        | (df["amount_inr"] <= 0)
    )

    print(
        "08_investor_transactions: invalid amounts =",
        invalid_amount.sum()
    )

    # Validate KYC status
    valid_kyc_values = {
        "Verified",
        "Pending",
        "Rejected"
    }

    invalid_kyc = ~df[
        "kyc_status"
    ].isin(valid_kyc_values)

    print(
        "08_investor_transactions: invalid KYC values =",
        invalid_kyc.sum()
    )

    df = remove_duplicates(
        df,
        "08_investor_transactions"
    )

    output = PROCESSED_DIR / "08_investor_transactions.csv"

    df.to_csv(output, index=False)

    print(
        f"08_investor_transactions → "
        f"{len(df):,} rows"
    )

    return df


# ============================================================
# 09 - PORTFOLIO HOLDINGS
# ============================================================

def clean_portfolio_holdings():

    file = find_file("09")
    df = pd.read_csv(file)

    df = clean_text_columns(df)

    df["portfolio_date"] = pd.to_datetime(
        df["portfolio_date"],
        errors="coerce"
    )

    numeric_columns = [
        "weight_pct",
        "market_value_cr",
        "current_price_inr"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = remove_duplicates(
        df,
        "09_portfolio_holdings"
    )

    output = PROCESSED_DIR / "09_portfolio_holdings.csv"

    df.to_csv(output, index=False)

    print(f"09_portfolio_holdings → {len(df):,} rows")

    return df


# ============================================================
# 10 - BENCHMARK INDICES
# ============================================================

def clean_benchmark_indices():

    file = find_file("10")
    df = pd.read_csv(file)

    df = clean_text_columns(df)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["close_value"] = pd.to_numeric(
        df["close_value"],
        errors="coerce"
    )

    df = remove_duplicates(
        df,
        "10_benchmark_indices"
    )

    df = df.sort_values(
        ["index_name", "date"]
    ).reset_index(drop=True)

    output = PROCESSED_DIR / "10_benchmark_indices.csv"

    df.to_csv(output, index=False)

    print(f"10_benchmark_indices → {len(df):,} rows")

    return df


# ============================================================
# RUN ALL CLEANING
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("BLUESTOCK MUTUAL FUND DATA CLEANING STARTED")
    print("=" * 70)

    clean_fund_master()
    clean_nav_history()
    clean_aum_by_fund_house()
    clean_monthly_sip()
    clean_category_inflows()
    clean_industry_folio()
    clean_scheme_performance()
    clean_investor_transactions()
    clean_portfolio_holdings()
    clean_benchmark_indices()

    print("\n")
    print("=" * 70)
    print("DATA CLEANING COMPLETE")
    print("=" * 70)

    processed_files = sorted(
        PROCESSED_DIR.glob("*.csv")
    )

    print(
        f"\nProcessed CSV files created: "
        f"{len(processed_files)}"
    )

    for file in processed_files:
        df = pd.read_csv(file)
        print(
            f"  ✓ {file.name:<40} "
            f"{len(df):,} rows"
        )

    print("\nAll cleaned files are in:")
    print(PROCESSED_DIR.resolve())


if __name__ == "__main__":
    main()