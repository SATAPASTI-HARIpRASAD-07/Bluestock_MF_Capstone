import logging
from pathlib import Path
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHARTS_DIR = BASE_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
VIS_DIR = BASE_DIR / "visualizations"
VIS_DIR.mkdir(parents=True, exist_ok=True)

# Set clean styling for charts
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
sns.set_theme(style="whitegrid")

def generate_all_charts():
    logger.info("Generating 15+ EDA, Performance, and Risk charts into charts/ directory...")
    
    # Load processed CSVs
    df_master = pd.read_csv(PROCESSED_DIR / "01_fund_master.csv")
    df_nav = pd.read_csv(PROCESSED_DIR / "02_nav_history.csv")
    df_aum = pd.read_csv(PROCESSED_DIR / "03_aum_by_fund_house.csv")
    df_sip = pd.read_csv(PROCESSED_DIR / "04_monthly_sip_inflows.csv")
    df_cat_inflow = pd.read_csv(PROCESSED_DIR / "05_category_inflows.csv")
    df_folio = pd.read_csv(PROCESSED_DIR / "06_industry_folio_count.csv")
    df_perf = pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv")
    df_tx = pd.read_csv(PROCESSED_DIR / "08_investor_transactions.csv")
    df_port = pd.read_csv(PROCESSED_DIR / "09_portfolio_holdings.csv")
    df_bm = pd.read_csv(PROCESSED_DIR / "10_benchmark_indices.csv")

    # 1. NAV Trend Chart
    plt.figure(figsize=(12, 6))
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    sample_codes = df_nav["amfi_code"].unique()[:5]
    for code in sample_codes:
        sub = df_nav[df_nav["amfi_code"] == code]
        name = df_master[df_master["amfi_code"] == code]["scheme_name"].values
        label_str = name[0] if len(name) > 0 else f"Scheme {code}"
        plt.plot(sub["date"], sub["nav"], label=label_str[:30])
    plt.title("1. Historical NAV Trajectory (Top Sample Schemes)", fontsize=14, fontweight="bold")
    plt.xlabel("Date")
    plt.ylabel("Net Asset Value (INR)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "nav_trend.png", dpi=300)
    plt.close()

    # 2. AUM Growth by Fund House
    plt.figure(figsize=(12, 6))
    top_aum = df_aum.groupby("fund_house")["aum_crore"].mean().sort_values(ascending=False).head(10)
    sns.barplot(x=top_aum.values, y=top_aum.index, palette="Blues_r")
    plt.title("2. Average AUM by Fund House (INR Crore)", fontsize=14, fontweight="bold")
    plt.xlabel("Average AUM (INR Crore)")
    plt.ylabel("Fund House")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "aum_growth.png", dpi=300)
    plt.close()

    # 3. SIP Inflow Trend
    plt.figure(figsize=(12, 6))
    df_sip["month"] = pd.to_datetime(df_sip["month"])
    df_sip_sorted = df_sip.sort_values("month")
    plt.plot(df_sip_sorted["month"], df_sip_sorted["sip_inflow_crore"], marker="o", color="#1f77b4", linewidth=2.5)
    plt.title("3. Monthly Industry SIP Inflow Trend (INR Crore)", fontsize=14, fontweight="bold")
    plt.xlabel("Month")
    plt.ylabel("SIP Inflow (INR Crore)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "sip_inflow_trend.png", dpi=300)
    plt.close()

    # 4. Category Inflow Heatmap
    plt.figure(figsize=(12, 6))
    pivot_cat = df_cat_inflow.pivot(index="category", columns="month", values="net_inflow_crore").fillna(0)
    sns.heatmap(pivot_cat.iloc[:, -12:], cmap="YlGnBu", annot=False, fmt=".0f", cbar_kws={"label": "Net Inflow (Cr)"})
    plt.title("4. Category-Wise Net Monthly Inflow Heatmap (Last 12 Months)", fontsize=14, fontweight="bold")
    plt.xlabel("Month")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "category_inflow_heatmap.png", dpi=300)
    plt.close()

    # 5. Investor Age Distribution
    plt.figure(figsize=(10, 6))
    age_counts = df_tx["age_group"].value_counts()
    sns.barplot(x=age_counts.index, y=age_counts.values, palette="Set2")
    plt.title("5. Investor Transaction Count by Age Group", fontsize=14, fontweight="bold")
    plt.xlabel("Age Group")
    plt.ylabel("Number of Transactions")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "investor_age_distribution.png", dpi=300)
    plt.close()

    # 6. SIP Amount by Age Group
    plt.figure(figsize=(10, 6))
    sip_tx = df_tx[df_tx["transaction_type"] == "SIP"]
    avg_sip_age = sip_tx.groupby("age_group")["amount_inr"].mean()
    sns.barplot(x=avg_sip_age.index, y=avg_sip_age.values, palette="Purples_r")
    plt.title("6. Average Monthly SIP Amount by Age Group (INR)", fontsize=14, fontweight="bold")
    plt.xlabel("Age Group")
    plt.ylabel("Average SIP Amount (INR)")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "sip_by_age_group.png", dpi=300)
    plt.close()

    # 7. Geographic Transaction Distribution
    plt.figure(figsize=(12, 6))
    top_states = df_tx.groupby("state")["amount_inr"].sum().sort_values(ascending=False).head(10) / 1e7 # in Cr
    sns.barplot(x=top_states.values, y=top_states.index, palette="viridis")
    plt.title("7. Top 10 States by Total Transaction Volume (INR Cr)", fontsize=14, fontweight="bold")
    plt.xlabel("Total Transaction Volume (INR Crore)")
    plt.ylabel("State")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "geographic_transactions.png", dpi=300)
    plt.close()

    # 8. T30 vs B30 Volume Comparison
    plt.figure(figsize=(8, 6))
    tier_counts = df_tx["city_tier"].value_counts()
    plt.pie(tier_counts.values, labels=tier_counts.index, autopct="%1.1f%%", colors=["#2ca02c", "#ff7f0e"], startangle=90, explode=(0.05, 0))
    plt.title("8. Investor Transaction Distribution: T30 vs B30 Cities", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "t30_vs_b30.png", dpi=300)
    plt.close()

    # 9. Industry Folio Count Growth
    plt.figure(figsize=(12, 6))
    df_folio["month"] = pd.to_datetime(df_folio["month"])
    df_folio_sorted = df_folio.sort_values("month")
    plt.plot(df_folio_sorted["month"], df_folio_sorted["total_folios_crore"], label="Total Folios", marker="o", color="purple")
    if "equity_folios_crore" in df_folio_sorted.columns:
        plt.plot(df_folio_sorted["month"], df_folio_sorted["equity_folios_crore"], label="Equity Folios", linestyle="--", color="green")
    plt.title("9. Industry Mutual Fund Folio Count Trajectory (Crore)", fontsize=14, fontweight="bold")
    plt.xlabel("Month")
    plt.ylabel("Folios (Crore)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "folio_count_growth.png", dpi=300)
    plt.close()

    # 10. NAV Return Correlation Matrix
    plt.figure(figsize=(8, 6))
    corr_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "sharpe_ratio", "alpha", "beta", "expense_ratio_pct", "max_drawdown_pct"]
    corr_matrix = df_perf[[c for c in corr_cols if c in df_perf.columns]].corr()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("10. Fund Performance Metrics Correlation Matrix", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "nav_return_correlation.png", dpi=300)
    plt.close()

    # 11. Top Portfolio Sector Allocations
    plt.figure(figsize=(10, 6))
    top_sec = df_port.groupby("sector")["weight_pct"].mean().sort_values(ascending=False).head(10)
    sns.barplot(x=top_sec.values, y=top_sec.index, palette="Oranges_r")
    plt.title("11. Average Mutual Fund Portfolio Sector Allocation (%)", fontsize=14, fontweight="bold")
    plt.xlabel("Average Portfolio Weight (%)")
    plt.ylabel("Sector")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "sector_allocation.png", dpi=300)
    plt.close()

    # 12. Fund Category Distribution
    plt.figure(figsize=(10, 6))
    cat_counts = df_master["category"].value_counts()
    sns.barplot(x=cat_counts.values, y=cat_counts.index, palette="crest")
    plt.title("12. Mutual Fund Scheme Count by Category", fontsize=14, fontweight="bold")
    plt.xlabel("Number of Schemes")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "fund_category_distribution.png", dpi=300)
    plt.close()

    # 13. Transaction Type Distribution
    plt.figure(figsize=(10, 6))
    tx_type_vol = df_tx.groupby("transaction_type")["amount_inr"].sum() / 1e7
    sns.barplot(x=tx_type_vol.index, y=tx_type_vol.values, palette="magma")
    plt.title("13. Total Transaction Volume by Type (INR Crore)", fontsize=14, fontweight="bold")
    plt.xlabel("Transaction Type")
    plt.ylabel("Total Volume (INR Crore)")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "transaction_type_distribution.png", dpi=300)
    plt.close()

    # 14. Fund House Comparison (Schemes vs AUM)
    plt.figure(figsize=(12, 6))
    fh_comp = df_master["fund_house"].value_counts().head(10)
    sns.barplot(x=fh_comp.values, y=fh_comp.index, palette="mako")
    plt.title("14. Top 10 Fund Houses by Scheme Count", fontsize=14, fontweight="bold")
    plt.xlabel("Number of Schemes Managed")
    plt.ylabel("Fund House")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "fund_house_comparison.png", dpi=300)
    plt.close()

    # 15. Risk vs Return Relationship Scatter
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df_perf,
        x="std_dev_ann_pct",
        y="return_3yr_pct",
        hue="category",
        style="risk_grade" if "risk_grade" in df_perf.columns else None,
        s=120,
        palette="tab10"
    )
    plt.title("15. Risk (Annualized Std Dev) vs Return (3-Year CAGR %)", fontsize=14, fontweight="bold")
    plt.xlabel("Annualized Volatility / Std Dev (%)")
    plt.ylabel("3-Year CAGR Return (%)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "risk_return_relationship.png", dpi=300)
    plt.close()

    # 16. Rolling Sharpe Ratio Chart (Day 6 Advanced Analytics)
    plt.figure(figsize=(12, 6))
    df_nav_sample = df_nav[df_nav["amfi_code"].isin(sample_codes[:3])].copy()
    df_nav_sample["daily_ret"] = df_nav_sample.groupby("amfi_code")["nav"].pct_change()
    
    for code, group in df_nav_sample.groupby("amfi_code"):
        group = group.sort_values("date").copy()
        # 90-day rolling Sharpe
        roll_mean = group["daily_ret"].rolling(90).mean() * 252
        roll_std = group["daily_ret"].rolling(90).std() * np.sqrt(252)
        group["rolling_sharpe"] = (roll_mean - 0.065) / roll_std
        
        name = df_master[df_master["amfi_code"] == code]["scheme_name"].values
        label_str = name[0] if len(name) > 0 else f"Scheme {code}"
        plt.plot(group["date"], group["rolling_sharpe"], label=label_str[:30])

    plt.title("16. 90-Day Rolling Sharpe Ratio Trajectory", fontsize=14, fontweight="bold")
    plt.xlabel("Date")
    plt.ylabel("Rolling 90-Day Sharpe Ratio")
    plt.axhline(0, color="gray", linestyle="--", alpha=0.7)
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "rolling_sharpe_chart.png", dpi=300)
    plt.close()

    # Copy files to visualizations/ directory as well for backwards compatibility
    for chart_file in CHARTS_DIR.glob("*.png"):
        (VIS_DIR / chart_file.name).write_bytes(chart_file.read_bytes())

    logger.info("Successfully generated and saved all 16 charts into charts/ and visualizations/")

if __name__ == "__main__":
    generate_all_charts()
