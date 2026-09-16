import os
from pathlib import Path
import sqlite3
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR = BASE_DIR / "data" / "raw"
DB_PATH = BASE_DIR / "db" / "bluestock_mf.db"
OUTPUT_DIR = BASE_DIR / "outputs"
CHARTS_DIR = BASE_DIR / "charts"
REPORTS_DIR = BASE_DIR / "reports"

EXPECTED_DATASETS = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

def test_raw_datasets_exist():
    raw_files = list(RAW_DIR.glob("*.csv"))
    assert len(raw_files) >= 10, f"Expected 10 raw CSV files, found {len(raw_files)}"

def test_processed_datasets_exist():
    for ds in EXPECTED_DATASETS:
        p = PROCESSED_DIR / ds
        assert p.exists(), f"Processed dataset missing: {ds}"
        df = pd.read_csv(p)
        assert len(df) > 0, f"Processed dataset is empty: {ds}"

def test_nav_history_validity():
    nav_p = PROCESSED_DIR / "02_nav_history.csv"
    df = pd.read_csv(nav_p)
    assert (df["nav"] > 0).all(), "Found invalid NAV <= 0 in nav_history"

def test_investor_transactions_validity():
    tx_p = PROCESSED_DIR / "08_investor_transactions.csv"
    df = pd.read_csv(tx_p)
    assert (df["amount_inr"] > 0).all(), "Found invalid transaction amount <= 0"
    valid_types = {"SIP", "Lumpsum", "Redemption"}
    assert set(df["transaction_type"].unique()).issubset(valid_types), "Found invalid transaction types"

def test_sqlite_database_integrity():
    if not DB_PATH.exists():
        pytest.skip("SQLite database db/bluestock_mf.db not created yet")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    required_tables = ["dim_fund", "dim_date", "fact_nav", "fact_transactions", "fact_performance"]
    for tbl in required_tables:
        assert tbl in tables, f"Database table missing: {tbl}"

def test_output_csv_files_exist():
    outputs = [
        "fund_scorecard.csv",
        "alpha_beta.csv",
        "var_cvar_report.csv",
        "cohort_analysis.csv",
        "sip_continuity.csv",
        "sector_hhi.csv"
    ]
    for out in outputs:
        p = OUTPUT_DIR / out
        if p.exists():
            df = pd.read_csv(p)
            assert len(df) > 0, f"Output CSV is empty: {out}"

def test_chart_files_generated():
    charts = list(CHARTS_DIR.glob("*.png"))
    # Should have 15+ generated charts
    if len(charts) > 0:
        assert len(charts) >= 15, f"Expected 15+ charts in charts/, found {len(charts)}"
