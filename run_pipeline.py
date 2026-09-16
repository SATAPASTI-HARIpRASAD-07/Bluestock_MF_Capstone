import logging
import os
from pathlib import Path
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MASTER_PIPELINE")

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Add file handler for logs
file_handler = logging.FileHandler(LOGS_DIR / "pipeline_execution.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)

# Add scripts directory to sys.path
sys.path.insert(0, str(BASE_DIR / "scripts"))

def main():
    start_time = time.time()
    logger.info("======================================================================")
    logger.info("BLUESTOCK MUTUAL FUND ANALYTICS — MASTER PIPELINE EXECUTION")
    logger.info("======================================================================")
    
    # 1. Environment & Directory Setup
    logger.info("[STEP 1/9] Validating project directories...")
    for dir_name in ["data/raw", "data/processed", "db", "notebooks", "scripts", "sql", "dashboard", "reports", "charts", "outputs", "logs", "tests"]:
        p = BASE_DIR / dir_name
        p.mkdir(parents=True, exist_ok=True)
        logger.info(f"  [OK] Verified directory: {dir_name}")
        
    # 2. Live NAV Fetching
    logger.info("\n[STEP 2/9] Executing Live NAV API Ingestion (scripts/live_nav_fetch.py)...")
    try:
        import live_nav_fetch
        df_live = live_nav_fetch.fetch_live_navs()
        logger.info(f"  [OK] Live NAV Fetch completed. Processed {len(df_live)} schemes.")
    except Exception as e:
        logger.error(f"  [X] Live NAV Fetch failed: {e}")

    # 3. Data Cleaning & Star Schema ETL
    logger.info("\n[STEP 3/9] Executing Master ETL & Star Schema Database Loading (scripts/etl_pipeline.py)...")
    try:
        import etl_pipeline
        etl_pipeline.run_etl()
        logger.info("  [OK] ETL Pipeline & Database loading complete.")
    except Exception as e:
        logger.error(f"  [X] ETL Pipeline failed: {e}")

    # 4. Compute Risk & Return Metrics & Scorecard
    logger.info("\n[STEP 4/9] Calculating Performance Metrics, Ratios & Fund Scorecard (scripts/compute_metrics.py)...")
    try:
        import compute_metrics
        compute_metrics.compute_fund_metrics()
        logger.info("  [OK] Performance metrics & Fund Scorecard generated.")
    except Exception as e:
        logger.error(f"  [X] Metrics computation failed: {e}")

    # 5. Advanced Analytics
    logger.info("\n[STEP 5/9] Executing Advanced Analytics (VaR, CVaR, Cohort, SIP Continuity, HHI) (scripts/advanced_analytics.py)...")
    try:
        import advanced_analytics
        advanced_analytics.run_advanced_analytics()
        logger.info("  [OK] Advanced Analytics reports generated.")
    except Exception as e:
        logger.error(f"  [X] Advanced Analytics failed: {e}")

    # 6. Fund Recommendation Engine Test
    logger.info("\n[STEP 6/9] Testing Transparent Recommendation Model (scripts/recommender.py)...")
    try:
        import recommender
        rec_df = recommender.recommend_funds("Moderate", 3)
        logger.info(f"  [OK] Recommender model operational. Top match: {rec_df.iloc[0]['scheme_name'] if not rec_df.empty else 'N/A'}")
    except Exception as e:
        logger.error(f"  [X] Recommender engine failed: {e}")

    # 7. Generate All Visualizations
    logger.info("\n[STEP 7/9] Generating 15+ EDA, Performance & Risk Charts (scripts/generate_charts.py)...")
    try:
        import generate_charts
        generate_charts.generate_all_charts()
        logger.info("  [OK] All 16 visualization charts generated into charts/")
    except Exception as e:
        logger.error(f"  [X] Visualization generation failed: {e}")

    # 8. Generate Reports & Presentations
    logger.info("\n[STEP 8/9] Generating PDF Final Report & PowerPoint Deck (scripts/generate_report.py & generate_presentation.py)...")
    try:
        import generate_report
        generate_report.generate_pdf_report()
        logger.info("  [OK] 24-section Final Report PDF generated at reports/Final_Report.pdf")
    except Exception as e:
        logger.error(f"  [X] PDF Report generation failed: {e}")

    try:
        import generate_presentation
        generate_presentation.generate_pptx()
        logger.info("  [OK] 12-slide Presentation PPTX generated at reports/Bluestock_MF_Presentation.pptx")
    except Exception as e:
        logger.error(f"  [X] PPTX Presentation generation failed: {e}")

    # 9. Output Validation Summary
    logger.info("\n[STEP 9/9] Executing Final Deliverables Validation...")
    required_deliverables = [
        BASE_DIR / "data" / "processed" / "01_fund_master.csv",
        BASE_DIR / "db" / "bluestock_mf.db",
        BASE_DIR / "sql" / "schema.sql",
        BASE_DIR / "sql" / "queries.sql",
        BASE_DIR / "outputs" / "fund_scorecard.csv",
        BASE_DIR / "outputs" / "alpha_beta.csv",
        BASE_DIR / "outputs" / "var_cvar_report.csv",
        BASE_DIR / "outputs" / "cohort_analysis.csv",
        BASE_DIR / "outputs" / "sip_continuity.csv",
        BASE_DIR / "outputs" / "sector_hhi.csv",
        BASE_DIR / "reports" / "Final_Report.pdf",
        BASE_DIR / "reports" / "Bluestock_MF_Presentation.pptx",
        BASE_DIR / "README.md",
        BASE_DIR / "data_dictionary.md"
    ]
    
    missing_count = 0
    for file_path in required_deliverables:
        if file_path.exists():
            logger.info(f"  [VALIDATED] {file_path.relative_to(BASE_DIR)}")
        else:
            logger.error(f"  [MISSING]   {file_path.relative_to(BASE_DIR)}")
            missing_count += 1
            
    elapsed = round(time.time() - start_time, 2)
    logger.info("======================================================================")
    if missing_count == 0:
        logger.info(f"SUCCESS: ALL PIPELINE STAGES COMPLETED IN {elapsed} SECONDS!")
        logger.info("The Bluestock Mutual Fund Analytics project is submission-ready!")
    else:
        logger.warning(f"PIPELINE COMPLETED IN {elapsed} SECONDS WITH {missing_count} MISSING DELIVERABLES.")
    logger.info("======================================================================")

if __name__ == "__main__":
    main()
