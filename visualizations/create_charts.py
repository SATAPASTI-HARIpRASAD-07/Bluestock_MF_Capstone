import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
# ============================================================
# PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "bluestock_mf.db"
OUTPUT_DIR = BASE_DIR / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)
# ============================================================
# DATABASE CONNECTION
# ============================================================
def get_connection():
    return sqlite3.connect(DB_PATH)
# ============================================================
# 1. CATEGORY PERFORMANCE
# ============================================================
def chart_category_performance(conn):
    query = """
    SELECT
        category,
        ROUND(AVG(return_3yr_pct), 2) AS avg_3yr_return
    FROM scheme_performance
    GROUP BY category
    ORDER BY avg_3yr_return DESC;
    """
    df = pd.read_sql_query(query, conn)
    plt.figure(figsize=(12, 7))
    plt.bar(
        df["category"],
        df["avg_3yr_return"]
    )
    plt.title("Average 3-Year Return by Mutual Fund Category")
    plt.xlabel("Category")
    plt.ylabel("Average 3-Year Return (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    output = OUTPUT_DIR / "category_performance.png"
    plt.savefig(output, dpi=300)
    plt.close()
    print(f"Created: {output}")
# ============================================================
# 2. TOP 10 FUNDS BY 3-YEAR RETURN
# ============================================================
def chart_top_funds(conn):
    query = """
    SELECT
        scheme_name,
        ROUND(return_3yr_pct, 2) AS return_3yr_pct
    FROM scheme_performance
    ORDER BY return_3yr_pct DESC
    LIMIT 10;
    """
    df = pd.read_sql_query(query, conn)
    df = df.sort_values("return_3yr_pct")
    plt.figure(figsize=(12, 7))
    plt.barh(
        df["scheme_name"],
        df["return_3yr_pct"]
    )
    plt.title("Top 10 Mutual Funds by 3-Year Return")
    plt.xlabel("3-Year Return (%)")
    plt.ylabel("Fund")
    plt.tight_layout()
    output = OUTPUT_DIR / "top_10_funds.png"
    plt.savefig(output, dpi=300)
    plt.close()
    print(f"Created: {output}")
# ============================================================
# 3. FUND HOUSE AUM
# ============================================================
def chart_fund_house_aum(conn):
    query = """
    SELECT
        fund_house,
        ROUND(AVG(aum_crore), 2) AS avg_aum_crore
    FROM aum_by_fund_house
    GROUP BY fund_house
    ORDER BY avg_aum_crore DESC;
    """
    df = pd.read_sql_query(query, conn)
    plt.figure(figsize=(12, 7))
    plt.bar(
        df["fund_house"],
        df["avg_aum_crore"]
    )
    plt.title("Average AUM by Fund House")
    plt.xlabel("Fund House")
    plt.ylabel("Average AUM (Crore)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    output = OUTPUT_DIR / "fund_house_aum.png"
    plt.savefig(output, dpi=300)
    plt.close()
    print(f"Created: {output}")
# ============================================================
# 4. CATEGORY-WISE NET INFLOW
# ============================================================
def chart_category_inflow(conn):
    query = """
    SELECT
        category,
        ROUND(SUM(net_inflow_crore), 2) AS total_net_inflow_crore
    FROM category_inflows
    GROUP BY category
    ORDER BY total_net_inflow_crore DESC;
    """
    df = pd.read_sql_query(query, conn)
    plt.figure(figsize=(12, 7))
    plt.bar(
        df["category"],
        df["total_net_inflow_crore"]
    )
    plt.title("Category-Wise Net Inflow")
    plt.xlabel("Category")
    plt.ylabel("Net Inflow (Crore)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    output = OUTPUT_DIR / "category_net_inflow.png"
    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Created: {output}")
# ============================================================
# 5. MONTHLY SIP INFLOW TREND
# ============================================================
def chart_sip_trend(conn):
    query = """
    SELECT
        month,
        sip_inflow_crore,
        active_sip_accounts_crore,
        new_sip_accounts_lakh,
        sip_aum_lakh_crore,
        yoy_growth_pct
    FROM monthly_sip_inflows
    ORDER BY month;
    """
    df = pd.read_sql_query(query, conn)
    df["month"] = pd.to_datetime(df["month"])
    plt.figure(figsize=(14, 7))
    plt.plot(
        df["month"],
        df["sip_inflow_crore"],
        marker="o"
    )
    plt.title("Monthly SIP Inflow Trend")
    plt.xlabel("Month")
    plt.ylabel("SIP Inflow (Crore)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    output = OUTPUT_DIR / "sip_inflow_trend.png"
    plt.savefig(output, dpi=300)
    plt.close()
    print(f"Created: {output}")
# ============================================================
# 6. TRANSACTION TYPE ANALYSIS
# ============================================================
def chart_transaction_types(conn):
    query = """
    SELECT
        transaction_type,
        COUNT(*) AS transaction_count
    FROM investor_transactions
    GROUP BY transaction_type
    ORDER BY transaction_count DESC;
    """
    df = pd.read_sql_query(query, conn)
    plt.figure(figsize=(9, 6))
    plt.bar(
        df["transaction_type"],
        df["transaction_count"]
    )
    plt.title("Investor Transactions by Transaction Type")
    plt.xlabel("Transaction Type")
    plt.ylabel("Number of Transactions")
    plt.tight_layout()
    output = OUTPUT_DIR / "transaction_types.png"
    plt.savefig(output, dpi=300)
    plt.close()
    print(f"Created: {output}")
# ============================================================
# 7. STATE-WISE INVESTOR TRANSACTIONS
# ============================================================
def chart_state_transactions(conn):
    query = """
    SELECT
        state,
        COUNT(*) AS transaction_count
    FROM investor_transactions
    GROUP BY state
    ORDER BY transaction_count DESC
    LIMIT 10;
    """
    df = pd.read_sql_query(query, conn)
    df = df.sort_values("transaction_count")
    plt.figure(figsize=(10, 7))
    plt.barh(
        df["state"],
        df["transaction_count"]
    )
    plt.title("Top 10 States by Investor Transactions")
    plt.xlabel("Number of Transactions")
    plt.ylabel("State")
    plt.tight_layout()
    output = OUTPUT_DIR / "state_transactions.png"
    plt.savefig(output, dpi=300)
    plt.close()
    print(f"Created: {output}")
# ============================================================
# 8. AVERAGE PORTFOLIO SECTOR EXPOSURE
# ============================================================
def chart_sector_exposure(conn):
    query = """
    SELECT
        sector,
        ROUND(AVG(weight_pct), 2) AS avg_weight_pct
    FROM portfolio_holdings
    GROUP BY sector
    ORDER BY avg_weight_pct DESC;
    """
    df = pd.read_sql_query(query, conn)
    plt.figure(figsize=(12, 7))
    plt.bar(
        df["sector"],
        df["avg_weight_pct"]
    )
    plt.title("Average Portfolio Sector Exposure")
    plt.xlabel("Sector")
    plt.ylabel("Average Weight (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    output = OUTPUT_DIR / "sector_exposure.png"
    plt.savefig(output, dpi=300)
    plt.close()
    print(f"Created: {output}")
# ============================================================
# MAIN PROGRAM
# ============================================================
def main():
    print("=" * 70)
    print("BLUESTOCK MUTUAL FUND VISUALIZATION")
    print("=" * 70)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Output folder: {OUTPUT_DIR}")
    conn = get_connection()
    chart_category_performance(conn)
    chart_top_funds(conn)
    chart_fund_house_aum(conn)
    chart_category_inflow(conn)
    chart_sip_trend(conn)
    chart_transaction_types(conn)
    chart_state_transactions(conn)
    chart_sector_exposure(conn)
    conn.close()
    print("\n" + "=" * 70)
    print("ALL VISUALIZATIONS CREATED SUCCESSFULLY")
    print("=" * 70)
if __name__ == "__main__":
    main()