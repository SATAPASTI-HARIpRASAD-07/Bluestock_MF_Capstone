import logging
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_DIR = BASE_DIR / "db"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "bluestock_mf.db"
ROOT_DB_PATH = BASE_DIR / "bluestock_mf.db"

def find_raw_file(dataset_num: str):
    matches = list(RAW_DIR.glob(f"*{dataset_num}_*.csv"))
    if not matches:
        raise FileNotFoundError(f"Could not find dataset number {dataset_num} in {RAW_DIR}")
    return matches[0]

def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df

def run_etl():
    logger.info("==================================================")
    logger.info("BLUESTOCK MUTUAL FUND ETL PIPELINE STARTED")
    logger.info("==================================================")
    
    cleaned_dfs = {}
    
    # 01 Fund Master
    logger.info("Processing 01_fund_master...")
    f1 = find_raw_file("01")
    df1 = clean_text_columns(pd.read_csv(f1)).drop_duplicates()
    df1["launch_date"] = pd.to_datetime(df1["launch_date"], errors="coerce")
    for col in ["expense_ratio_pct", "exit_load_pct", "min_sip_amount", "min_lumpsum_amount"]:
        df1[col] = pd.to_numeric(df1[col], errors="coerce")
    df1.to_csv(PROCESSED_DIR / "01_fund_master.csv", index=False)
    cleaned_dfs["01_fund_master"] = df1

    # 02 NAV History
    logger.info("Processing 02_nav_history...")
    f2 = find_raw_file("02")
    df2 = clean_text_columns(pd.read_csv(f2))
    df2["date"] = pd.to_datetime(df2["date"], errors="coerce")
    df2["nav"] = pd.to_numeric(df2["nav"], errors="coerce")
    df2 = df2.sort_values(["amfi_code", "date"]).drop_duplicates(subset=["amfi_code", "date"], keep="last")
    df2["nav"] = df2.groupby("amfi_code")["nav"].ffill()
    df2.to_csv(PROCESSED_DIR / "02_nav_history.csv", index=False)
    cleaned_dfs["02_nav_history"] = df2

    # 03 AUM by Fund House
    logger.info("Processing 03_aum_by_fund_house...")
    f3 = find_raw_file("03")
    df3 = clean_text_columns(pd.read_csv(f3)).drop_duplicates()
    df3["date"] = pd.to_datetime(df3["date"], errors="coerce")
    for col in ["aum_lakh_crore", "aum_crore", "num_schemes"]:
        df3[col] = pd.to_numeric(df3[col], errors="coerce")
    df3.to_csv(PROCESSED_DIR / "03_aum_by_fund_house.csv", index=False)
    cleaned_dfs["03_aum_by_fund_house"] = df3

    # 04 Monthly SIP Inflows
    logger.info("Processing 04_monthly_sip_inflows...")
    f4 = find_raw_file("04")
    df4 = clean_text_columns(pd.read_csv(f4)).drop_duplicates()
    df4["month"] = pd.to_datetime(df4["month"], format="%Y-%m", errors="coerce")
    for col in ["sip_inflow_crore", "active_sip_accounts_crore", "new_sip_accounts_lakh", "sip_aum_lakh_crore", "yoy_growth_pct"]:
        df4[col] = pd.to_numeric(df4[col], errors="coerce")
    df4.to_csv(PROCESSED_DIR / "04_monthly_sip_inflows.csv", index=False)
    cleaned_dfs["04_monthly_sip_inflows"] = df4

    # 05 Category Inflows
    logger.info("Processing 05_category_inflows...")
    f5 = find_raw_file("05")
    df5 = clean_text_columns(pd.read_csv(f5)).drop_duplicates()
    df5["month"] = pd.to_datetime(df5["month"], format="%Y-%m", errors="coerce")
    df5["net_inflow_crore"] = pd.to_numeric(df5["net_inflow_crore"], errors="coerce")
    df5.to_csv(PROCESSED_DIR / "05_category_inflows.csv", index=False)
    cleaned_dfs["05_category_inflows"] = df5

    # 06 Industry Folio Count
    logger.info("Processing 06_industry_folio_count...")
    f6 = find_raw_file("06")
    df6 = clean_text_columns(pd.read_csv(f6)).drop_duplicates()
    df6["month"] = pd.to_datetime(df6["month"], format="%Y-%m", errors="coerce")
    for col in ["total_folios_crore", "equity_folios_crore", "debt_folios_crore", "hybrid_folios_crore", "others_folios_crore"]:
        df6[col] = pd.to_numeric(df6[col], errors="coerce")
    df6.to_csv(PROCESSED_DIR / "06_industry_folio_count.csv", index=False)
    cleaned_dfs["06_industry_folio_count"] = df6

    # 07 Scheme Performance
    logger.info("Processing 07_scheme_performance...")
    f7 = find_raw_file("07")
    df7 = clean_text_columns(pd.read_csv(f7)).drop_duplicates()
    num_cols7 = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct", "aum_crore", "expense_ratio_pct", "morningstar_rating"]
    for col in num_cols7:
        df7[col] = pd.to_numeric(df7[col], errors="coerce")
    df7["anomaly_flag"] = df7["return_1yr_pct"].isna() | ~df7["expense_ratio_pct"].between(0.1, 2.5, inclusive="both")
    df7["anomaly_flag"] = df7["anomaly_flag"].astype(int)
    df7.to_csv(PROCESSED_DIR / "07_scheme_performance.csv", index=False)
    cleaned_dfs["07_scheme_performance"] = df7

    # 08 Investor Transactions
    logger.info("Processing 08_investor_transactions...")
    f8 = find_raw_file("08")
    df8 = clean_text_columns(pd.read_csv(f8)).drop_duplicates()
    df8["transaction_date"] = pd.to_datetime(df8["transaction_date"], errors="coerce")
    df8["amount_inr"] = pd.to_numeric(df8["amount_inr"], errors="coerce")
    tx_map = {"sip": "SIP", "SIP": "SIP", "lumpsum": "Lumpsum", "Lumpsum": "Lumpsum", "redemption": "Redemption", "Redemption": "Redemption"}
    df8["transaction_type"] = df8["transaction_type"].astype(str).str.strip().map(tx_map).fillna(df8["transaction_type"])
    df8.to_csv(PROCESSED_DIR / "08_investor_transactions.csv", index=False)
    cleaned_dfs["08_investor_transactions"] = df8

    # 09 Portfolio Holdings
    logger.info("Processing 09_portfolio_holdings...")
    f9 = find_raw_file("09")
    df9 = clean_text_columns(pd.read_csv(f9)).drop_duplicates()
    df9["portfolio_date"] = pd.to_datetime(df9["portfolio_date"], errors="coerce")
    for col in ["weight_pct", "market_value_cr", "current_price_inr"]:
        df9[col] = pd.to_numeric(df9[col], errors="coerce")
    df9.to_csv(PROCESSED_DIR / "09_portfolio_holdings.csv", index=False)
    cleaned_dfs["09_portfolio_holdings"] = df9

    # 10 Benchmark Indices
    logger.info("Processing 10_benchmark_indices...")
    f10 = find_raw_file("10")
    df10 = clean_text_columns(pd.read_csv(f10)).drop_duplicates()
    df10["date"] = pd.to_datetime(df10["date"], errors="coerce")
    df10["close_value"] = pd.to_numeric(df10["close_value"], errors="coerce")
    df10 = df10.sort_values(["index_name", "date"]).reset_index(drop=True)
    df10.to_csv(PROCESSED_DIR / "10_benchmark_indices.csv", index=False)
    cleaned_dfs["10_benchmark_indices"] = df10

    logger.info("All 10 datasets successfully cleaned and saved to data/processed/")

    # Populate SQLite Database
    logger.info(f"Populating SQLite database at {DB_PATH} and {ROOT_DB_PATH}...")
    for target_db in [DB_PATH, ROOT_DB_PATH]:
        conn = sqlite3.connect(target_db)
        
        # Load legacy / flat tables
        table_map = {
            "01_fund_master": "fund_master",
            "02_nav_history": "nav_history",
            "03_aum_by_fund_house": "aum_by_fund_house",
            "04_monthly_sip_inflows": "monthly_sip_inflows",
            "05_category_inflows": "category_inflows",
            "06_industry_folio_count": "industry_folio_count",
            "07_scheme_performance": "scheme_performance",
            "08_investor_transactions": "investor_transactions",
            "09_portfolio_holdings": "portfolio_holdings",
            "10_benchmark_indices": "benchmark_indices",
        }
        for key, tbl in table_map.items():
            cleaned_dfs[key].to_sql(tbl, conn, if_exists="replace", index=False)
            
        # Load Star Schema Tables
        cleaned_dfs["01_fund_master"].to_sql("dim_fund", conn, if_exists="replace", index=False)
        cleaned_dfs["02_nav_history"].to_sql("fact_nav", conn, if_exists="replace", index=False)
        cleaned_dfs["03_aum_by_fund_house"].to_sql("fact_aum", conn, if_exists="replace", index=False)
        cleaned_dfs["04_monthly_sip_inflows"].to_sql("fact_sip_industry", conn, if_exists="replace", index=False)
        cleaned_dfs["05_category_inflows"].to_sql("fact_category_inflows", conn, if_exists="replace", index=False)
        cleaned_dfs["06_industry_folio_count"].to_sql("fact_industry_folio", conn, if_exists="replace", index=False)
        cleaned_dfs["07_scheme_performance"].to_sql("fact_performance", conn, if_exists="replace", index=False)
        cleaned_dfs["08_investor_transactions"].to_sql("fact_transactions", conn, if_exists="replace", index=False)
        cleaned_dfs["09_portfolio_holdings"].to_sql("fact_portfolio", conn, if_exists="replace", index=False)
        cleaned_dfs["10_benchmark_indices"].to_sql("fact_benchmark", conn, if_exists="replace", index=False)
        
        # Build dim_date from all dates
        all_dates = pd.concat([
            cleaned_dfs["02_nav_history"]["date"],
            cleaned_dfs["08_investor_transactions"]["transaction_date"],
            cleaned_dfs["10_benchmark_indices"]["date"]
        ]).dropna().unique()
        
        df_date = pd.DataFrame({"full_date": pd.to_datetime(all_dates)}).sort_values("full_date").reset_index(drop=True)
        df_date["date_key"] = df_date["full_date"].dt.strftime("%Y%m%d").astype(int)
        df_date["year"] = df_date["full_date"].dt.year
        df_date["quarter"] = df_date["full_date"].dt.quarter
        df_date["month"] = df_date["full_date"].dt.month
        df_date["month_name"] = df_date["full_date"].dt.strftime("%B")
        df_date["day"] = df_date["full_date"].dt.day
        df_date["day_of_week"] = df_date["full_date"].dt.dayofweek
        df_date.to_sql("dim_date", conn, if_exists="replace", index=False)
        
        conn.close()

    logger.info("ETL Pipeline completed successfully!")

if __name__ == "__main__":
    run_etl()
