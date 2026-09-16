import json
import logging
from pathlib import Path
import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Default scheme list for API testing (e.g., HDFC Top 100 AMFI code: 125497, SBI Bluechip: 119551, etc.)
SAMPLE_AMFI_CODES = [125497, 119551, 119598, 119552, 118636]

def fetch_live_nav_for_scheme(amfi_code: int):
    """
    Fetch live NAV data from mfapi.in API for a given AMFI scheme code.
    Returns parsed metadata and latest NAV data if successful, else None.
    """
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                meta = data.get("meta", {})
                latest = data["data"][0]
                prev = data["data"][1] if len(data["data"]) > 1 else latest
                
                nav_curr = float(latest["nav"])
                nav_prev = float(prev["nav"])
                pct_change = ((nav_curr - nav_prev) / nav_prev) * 100 if nav_prev > 0 else 0.0
                
                return {
                    "amfi_code": amfi_code,
                    "scheme_name": meta.get("scheme_name", "Unknown"),
                    "fund_house": meta.get("fund_house", "Unknown"),
                    "scheme_category": meta.get("scheme_category", "Unknown"),
                    "latest_date": latest["date"],
                    "latest_nav": nav_curr,
                    "previous_nav": nav_prev,
                    "day_change_pct": round(pct_change, 2),
                    "status": "LIVE_SUCCESS"
                }
    except Exception as e:
        logger.warning(f"Live NAV API call failed for AMFI {amfi_code}: {e}")
    return None

def fetch_live_navs():
    """
    Fetches live NAVs for sample schemes with fallback to local processed data.
    """
    logger.info("Executing Live NAV Fetcher (mfapi.in API Integration)...")
    results = []
    
    # Try fetching live data for sample AMFI codes
    for code in SAMPLE_AMFI_CODES:
        res = fetch_live_nav_for_scheme(code)
        if res:
            results.append(res)
    
    if results:
        df_live = pd.DataFrame(results)
        logger.info(f"Successfully fetched live NAV data for {len(df_live)} schemes.")
    else:
        logger.warning("API unavailable or offline. Activating local data fallback.")
        nav_file = PROCESSED_DIR / "02_nav_history.csv"
        master_file = PROCESSED_DIR / "01_fund_master.csv"
        
        if nav_file.exists() and master_file.exists():
            df_nav = pd.read_csv(nav_file)
            df_master = pd.read_csv(master_file)
            
            # Get latest NAV date per scheme
            df_latest = df_nav.sort_values(["amfi_code", "date"]).groupby("amfi_code").last().reset_index()
            df_merged = pd.merge(df_latest, df_master, on="amfi_code", how="inner")
            
            for _, row in df_merged.head(5).iterrows():
                results.append({
                    "amfi_code": row["amfi_code"],
                    "scheme_name": row["scheme_name"],
                    "fund_house": row["fund_house"],
                    "scheme_category": row.get("category", "N/A"),
                    "latest_date": str(row["date"]),
                    "latest_nav": float(row["nav"]),
                    "previous_nav": float(row["nav"]),
                    "day_change_pct": 0.0,
                    "status": "LOCAL_FALLBACK"
                })
            df_live = pd.DataFrame(results)
        else:
            df_live = pd.DataFrame(columns=["amfi_code", "scheme_name", "latest_nav", "status"])

    output_path = OUTPUT_DIR / "live_nav_summary.csv"
    df_live.to_csv(output_path, index=False)
    logger.info(f"Saved live NAV summary to {output_path}")
    return df_live

if __name__ == "__main__":
    df_res = fetch_live_navs()
    print(df_res)
