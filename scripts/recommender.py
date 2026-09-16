import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

DISCLAIMER = (
    "EDUCATIONAL & ANALYTICAL DISCLAIMER: This mutual fund recommendation system "
    "is a rule-based analytical demonstration built strictly for research and educational purposes. "
    "It DOES NOT constitute professional financial, investment, or legal advice. "
    "Past performance is no guarantee of future returns."
)

def recommend_funds(risk_profile: str = "Moderate", top_n: int = 3):
    """
    Rule-based transparent mutual fund recommendation engine.
    
    Parameters:
    - risk_profile: 'Low', 'Moderate', or 'High'
    - top_n: Number of recommendations to return (default: 3)
    
    Returns:
    - DataFrame of recommended funds with key metrics and rationale.
    """
    risk_profile = risk_profile.strip().title()
    
    perf_file = PROCESSED_DIR / "07_scheme_performance.csv"
    if not perf_file.exists():
        logger.error(f"Scheme performance data file not found at {perf_file}")
        return pd.DataFrame()
        
    df = pd.read_csv(perf_file)
    
    # Filter based on risk profile
    if risk_profile == "Low":
        # Target Low/Moderate risk categories, e.g. Debt, Liquid, Hybrid, Large Cap
        allowed_risks = ["Low", "Low to Moderate", "Moderate"]
        allowed_cats = ["Debt", "Liquid", "Hybrid", "Large Cap"]
        filtered = df[
            (df["risk_grade"].isin(allowed_risks)) | 
            (df["category"].isin(allowed_cats))
        ]
    elif risk_profile == "High":
        # Target High / Very High risk categories, e.g. Small Cap, Mid Cap, Equity
        allowed_risks = ["High", "Very High"]
        allowed_cats = ["Small Cap", "Mid Cap", "Equity", "Flexi Cap"]
        filtered = df[
            (df["risk_grade"].isin(allowed_risks)) | 
            (df["category"].isin(allowed_cats))
        ]
    else:  # Moderate (default)
        allowed_risks = ["Moderate", "Moderately High", "Low to Moderate"]
        filtered = df[df["risk_grade"].isin(allowed_risks)]
        if filtered.empty:
            filtered = df.copy()

    if filtered.empty:
        filtered = df.copy()

    # Score funds based on Sharpe ratio (60%) and 3-Year Return (40%)
    filtered = filtered.copy()
    filtered["sharpe_score"] = filtered["sharpe_ratio"].fillna(0)
    filtered["return_score"] = filtered["return_3yr_pct"].fillna(0)
    
    # Sort by Sharpe ratio descending, then 3-year return descending
    recommended = filtered.sort_values(
        by=["sharpe_ratio", "return_3yr_pct"],
        ascending=[False, False]
    ).head(top_n).copy()
    
    cols = ["scheme_name", "category", "fund_house", "plan", "return_3yr_pct", "sharpe_ratio", "risk_grade", "expense_ratio_pct"]
    res = recommended[[c for c in cols if c in recommended.columns]].reset_index(drop=True)
    
    res["recommendation_rationale"] = res.apply(
        lambda row: f"Top-ranked for {risk_profile} risk with 3Yr Return of {row.get('return_3yr_pct', 0)}% and Sharpe ratio of {row.get('sharpe_ratio', 0)}.",
        axis=1
    )
    
    return res

if __name__ == "__main__":
    print("==================================================")
    print("BLUESTOCK MUTUAL FUND RECOMMENDER ENGINE")
    print("==================================================")
    print(DISCLAIMER)
    print("\nSample Recommendation for 'Moderate' Risk Profile:")
    rec = recommend_funds("Moderate", 3)
    print(rec)
