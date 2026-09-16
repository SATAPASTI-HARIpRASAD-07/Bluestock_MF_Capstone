import logging
from pathlib import Path
import numpy as np
import pandas as pd
import sqlite3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = BASE_DIR / "db" / "bluestock_mf.db"

RISK_FREE_RATE = 0.065  # 6.5% annual risk-free rate assumption for India

def compute_fund_metrics():
    logger.info("Computing fund performance, risk metrics, benchmark comparisons, and scorecard...")
    
    # Load scheme performance dataset
    perf_file = PROCESSED_DIR / "07_scheme_performance.csv"
    nav_file = PROCESSED_DIR / "02_nav_history.csv"
    master_file = PROCESSED_DIR / "01_fund_master.csv"
    bm_file = PROCESSED_DIR / "10_benchmark_indices.csv"
    
    if not (perf_file.exists() and nav_file.exists() and master_file.exists()):
        logger.error("Required processed CSV files missing for computing metrics!")
        return
        
    df_perf = pd.read_csv(perf_file)
    df_nav = pd.read_csv(nav_file)
    df_master = pd.read_csv(master_file)
    df_bm = pd.read_csv(bm_file)
    
    # Calculate NAV daily returns and max drawdown per fund
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    df_nav = df_nav.sort_values(["amfi_code", "date"])
    
    drawdown_dict = {}
    sharpe_dict = {}
    sortino_dict = {}
    std_dev_dict = {}
    
    for amfi_code, group in df_nav.groupby("amfi_code"):
        group = group.copy()
        group["daily_return"] = group["nav"].pct_change()
        
        # Max Drawdown
        group["running_max"] = group["nav"].cummax()
        group["drawdown"] = (group["nav"] - group["running_max"]) / group["running_max"]
        max_dd = abs(group["drawdown"].min()) * 100.0 if not group["drawdown"].empty else 0.0
        drawdown_dict[amfi_code] = round(max_dd, 2)
        
        # Risk & Ratios (Daily annualized)
        clean_ret = group["daily_return"].dropna()
        if len(clean_ret) > 10:
            ann_mean = clean_ret.mean() * 252
            ann_std = clean_ret.std() * np.sqrt(252)
            downside_std = clean_ret[clean_ret < 0].std() * np.sqrt(252)
            
            sharpe = (ann_mean - RISK_FREE_RATE) / ann_std if ann_std > 0 else 0.0
            sortino = (ann_mean - RISK_FREE_RATE) / downside_std if downside_std > 0 else 0.0
            
            sharpe_dict[amfi_code] = round(sharpe, 2)
            sortino_dict[amfi_code] = round(sortino, 2)
            std_dev_dict[amfi_code] = round(ann_std * 100.0, 2)
            
    # Update df_perf with calculated metrics if missing or zero
    df_perf["max_drawdown_pct"] = df_perf["amfi_code"].map(drawdown_dict).fillna(df_perf["max_drawdown_pct"])
    df_perf["sharpe_ratio"] = df_perf["amfi_code"].map(sharpe_dict).fillna(df_perf["sharpe_ratio"])
    df_perf["sortino_ratio"] = df_perf["amfi_code"].map(sortino_dict).fillna(df_perf["sortino_ratio"])
    df_perf["std_dev_ann_pct"] = df_perf["amfi_code"].map(std_dev_dict).fillna(df_perf["std_dev_ann_pct"])
    
    # -------------------------------------------------------------
    # Fund Scorecard Calculation (0-100 composite score)
    # Weights: 30% 3yr return, 25% Sharpe, 20% Alpha, 15% Expense Ratio (inv), 10% Max Drawdown (inv)
    # -------------------------------------------------------------
    score_df = df_perf.copy()
    
    def min_max_scale(series, invert=False):
        min_v = series.min()
        max_v = series.max()
        if max_v == min_v:
            return pd.Series(50.0, index=series.index)
        if invert:
            return (max_v - series) / (max_v - min_v) * 100.0
        return (series - min_v) / (max_v - min_v) * 100.0

    s_return = min_max_scale(score_df["return_3yr_pct"].fillna(0))
    s_sharpe = min_max_scale(score_df["sharpe_ratio"].fillna(0))
    s_alpha = min_max_scale(score_df["alpha"].fillna(0))
    s_exp = min_max_scale(score_df["expense_ratio_pct"].fillna(1.0), invert=True)
    s_dd = min_max_scale(score_df["max_drawdown_pct"].fillna(0), invert=True)

    score_df["composite_score"] = (
        0.30 * s_return +
        0.25 * s_sharpe +
        0.20 * s_alpha +
        0.15 * s_exp +
        0.10 * s_dd
    ).round(2)

    score_df["rank"] = score_df["composite_score"].rank(ascending=False, method="min").astype(int)
    score_df = score_df.sort_values("rank").reset_index(drop=True)
    
    scorecard_cols = [
        "rank", "scheme_name", "category", "fund_house", "plan",
        "return_3yr_pct", "sharpe_ratio", "sortino_ratio", "alpha", "beta",
        "expense_ratio_pct", "max_drawdown_pct", "composite_score"
    ]
    df_scorecard = score_df[[col for col in scorecard_cols if col in score_df.columns]]
    
    scorecard_path = OUTPUT_DIR / "fund_scorecard.csv"
    df_scorecard.to_csv(scorecard_path, index=False)
    logger.info(f"Saved Fund Scorecard to {scorecard_path}")

    # -------------------------------------------------------------
    # Benchmark Analysis (Alpha / Beta Summary)
    # -------------------------------------------------------------
    alpha_beta_cols = [
        "scheme_name", "category", "fund_house", "benchmark_3yr_pct",
        "return_3yr_pct", "alpha", "beta", "sharpe_ratio", "std_dev_ann_pct"
    ]
    df_alpha_beta = df_perf[[col for col in alpha_beta_cols if col in df_perf.columns]].copy()
    df_alpha_beta["excess_return_pct"] = (df_alpha_beta["return_3yr_pct"] - df_alpha_beta["benchmark_3yr_pct"]).round(2)
    
    alpha_beta_path = OUTPUT_DIR / "alpha_beta.csv"
    df_alpha_beta.to_csv(alpha_beta_path, index=False)
    logger.info(f"Saved Alpha/Beta Benchmark report to {alpha_beta_path}")

    logger.info("Metrics calculation completed successfully!")
    return df_scorecard, df_alpha_beta

if __name__ == "__main__":
    compute_fund_metrics()
