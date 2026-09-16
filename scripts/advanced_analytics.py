import logging
from pathlib import Path
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_advanced_analytics():
    logger.info("Executing Advanced Analytics (VaR, CVaR, Cohort, SIP Continuity, HHI Index)...")
    
    # -------------------------------------------------------------
    # 1. Historical 95% VaR & CVaR
    # -------------------------------------------------------------
    df_nav = pd.read_csv(PROCESSED_DIR / "02_nav_history.csv")
    df_master = pd.read_csv(PROCESSED_DIR / "01_fund_master.csv")
    
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    df_nav = df_nav.sort_values(["amfi_code", "date"])
    df_nav["daily_return"] = df_nav.groupby("amfi_code")["nav"].pct_change()
    
    var_cvar_list = []
    for amfi_code, group in df_nav.groupby("amfi_code"):
        rets = group["daily_return"].dropna()
        if len(rets) > 20:
            var_95 = np.percentile(rets, 5) # 5th percentile
            cvar_95 = rets[rets <= var_95].mean() if len(rets[rets <= var_95]) > 0 else var_95
            
            scheme_name = df_master[df_master["amfi_code"] == amfi_code]["scheme_name"].values
            category = df_master[df_master["amfi_code"] == amfi_code]["category"].values
            
            var_cvar_list.append({
                "amfi_code": amfi_code,
                "scheme_name": scheme_name[0] if len(scheme_name) > 0 else f"Scheme {amfi_code}",
                "category": category[0] if len(category) > 0 else "N/A",
                "var_95_daily_pct": round(abs(var_95) * 100.0, 2),
                "cvar_95_daily_pct": round(abs(cvar_95) * 100.0, 2),
                "interpretation": f"95% confidence max 1-day loss is {round(abs(var_95)*100.0, 2)}%"
            })
            
    df_var_cvar = pd.DataFrame(var_cvar_list).sort_values("var_95_daily_pct", ascending=False)
    var_path = OUTPUT_DIR / "var_cvar_report.csv"
    df_var_cvar.to_csv(var_path, index=False)
    logger.info(f"Saved VaR & CVaR report to {var_path}")

    # -------------------------------------------------------------
    # 2. Investor Cohort Analysis
    # -------------------------------------------------------------
    df_tx = pd.read_csv(PROCESSED_DIR / "08_investor_transactions.csv")
    df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])
    
    # First transaction date per investor
    first_tx = df_tx.groupby("investor_id")["transaction_date"].min().reset_index()
    first_tx["cohort_year"] = first_tx["transaction_date"].dt.year
    
    df_tx_cohort = pd.merge(df_tx, first_tx[["investor_id", "cohort_year"]], on="investor_id")
    
    cohort_summary = df_tx_cohort.groupby("cohort_year").agg(
        cohort_size=("investor_id", "nunique"),
        total_transactions=("amount_inr", "count"),
        total_invested_cr=("amount_inr", lambda x: round(x.sum() / 1e7, 2)),
        avg_transaction_inr=("amount_inr", lambda x: round(x.mean(), 2)),
        sip_count=("transaction_type", lambda x: (x == "SIP").sum())
    ).reset_index()
    
    cohort_path = OUTPUT_DIR / "cohort_analysis.csv"
    cohort_summary.to_csv(cohort_path, index=False)
    logger.info(f"Saved Investor Cohort Analysis to {cohort_path}")

    # -------------------------------------------------------------
    # 3. SIP Continuity Analysis
    # -------------------------------------------------------------
    sip_txs = df_tx[df_tx["transaction_type"] == "SIP"].sort_values(["investor_id", "transaction_date"])
    
    sip_continuity_list = []
    for inv_id, group in sip_txs.groupby("investor_id"):
        if len(group) >= 6: # Filter for investors with 6+ SIP transactions
            dates = group["transaction_date"].sort_values()
            gaps = dates.diff().dt.days.dropna()
            avg_gap = gaps.mean() if len(gaps) > 0 else 30.0
            max_gap = gaps.max() if len(gaps) > 0 else 30.0
            
            is_at_risk = avg_gap > 35.0 or max_gap > 45.0
            
            sip_continuity_list.append({
                "investor_id": inv_id,
                "total_sips": len(group),
                "avg_gap_days": round(avg_gap, 1),
                "max_gap_days": round(max_gap, 1),
                "total_sip_amount_inr": group["amount_inr"].sum(),
                "status": "AT_RISK" if is_at_risk else "HEALTHY"
            })
            
    df_sip_cont = pd.DataFrame(sip_continuity_list)
    if not df_sip_cont.empty:
        df_sip_cont = df_sip_cont.sort_values("avg_gap_days", ascending=False)
    sip_path = OUTPUT_DIR / "sip_continuity.csv"
    df_sip_cont.to_csv(sip_path, index=False)
    logger.info(f"Saved SIP Continuity report to {sip_path}")

    # -------------------------------------------------------------
    # 4. Sector Concentration HHI Index
    # -------------------------------------------------------------
    df_port = pd.read_csv(PROCESSED_DIR / "09_portfolio_holdings.csv")
    
    hhi_list = []
    for amfi_code, group in df_port.groupby("amfi_code"):
        # HHI = sum(weight_i ^ 2)
        weights = group["weight_pct"]
        hhi = (weights ** 2).sum()
        
        scheme_name = df_master[df_master["amfi_code"] == amfi_code]["scheme_name"].values
        top_sector = group.groupby("sector")["weight_pct"].sum().idxmax()
        
        # Classification
        if hhi > 2500:
            conc = "High Concentration"
        elif hhi > 1500:
            conc = "Moderate Concentration"
        else:
            conc = "Well Diversified"
            
        hhi_list.append({
            "amfi_code": amfi_code,
            "scheme_name": scheme_name[0] if len(scheme_name) > 0 else f"Scheme {amfi_code}",
            "hhi_index": round(hhi, 2),
            "dominant_sector": top_sector,
            "concentration_level": conc
        })
        
    df_hhi = pd.DataFrame(hhi_list).sort_values("hhi_index", ascending=False)
    hhi_path = OUTPUT_DIR / "sector_hhi.csv"
    df_hhi.to_csv(hhi_path, index=False)
    logger.info(f"Saved Sector Concentration HHI report to {hhi_path}")

    logger.info("Advanced Analytics completed successfully!")

if __name__ == "__main__":
    run_advanced_analytics()
