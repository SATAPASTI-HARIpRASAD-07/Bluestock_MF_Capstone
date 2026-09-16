import logging
from pathlib import Path
import sqlite3
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
DASHBOARD_DATA_DIR = BASE_DIR / "dashboard" / "data"
DASHBOARD_DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "db" / "bluestock_mf.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "bluestock_mf.db"

def prepare_dashboard_datasets():
    logger.info("Preparing dashboard-ready data sources in dashboard/data/...")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Export Star Schema tables from SQLite DB into dashboard/data/
    tables = [
        ("dim_fund", "dim_fund.csv"),
        ("dim_date", "dim_date.csv"),
        ("fact_nav", "fact_nav.csv"),
        ("fact_transactions", "fact_transactions.csv"),
        ("fact_performance", "fact_performance.csv"),
        ("fact_aum", "fact_aum.csv"),
        ("fact_portfolio", "fact_portfolio.csv"),
        ("fact_sip_industry", "fact_sip_industry.csv"),
        ("fact_category_inflows", "fact_category_inflows.csv"),
        ("fact_industry_folio", "fact_industry_folio.csv"),
        ("fact_benchmark", "fact_benchmark.csv")
    ]
    
    for tbl, filename in tables:
        try:
            df = pd.read_sql(f'SELECT * FROM "{tbl}"', conn)
            out_file = DASHBOARD_DATA_DIR / filename
            df.to_csv(out_file, index=False)
            logger.info(f"  ✓ Exported {tbl} -> dashboard/data/{filename} ({len(df):,} rows)")
        except Exception as e:
            logger.warning(f"  ✗ Could not export {tbl}: {e}")

    conn.close()
    
    # Also copy analytical output CSVs into dashboard/data/
    for out_name in ["fund_scorecard.csv", "alpha_beta.csv", "var_cvar_report.csv", "cohort_analysis.csv", "sip_continuity.csv", "sector_hhi.csv"]:
        src = OUTPUT_DIR / out_name
        if src.exists():
            df = pd.read_csv(src)
            df.to_csv(DASHBOARD_DATA_DIR / out_name, index=False)
            logger.info(f"  ✓ Exported output dataset -> dashboard/data/{out_name} ({len(df):,} rows)")

    logger.info("Dashboard data preparation complete!")

if __name__ == "__main__":
    prepare_dashboard_datasets()
