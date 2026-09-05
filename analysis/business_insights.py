import sqlite3
DB_PATH = "../bluestock_mf.db"
def main():
    conn = sqlite3.connect(DB_PATH)
    print("=" * 70)
    print("BLUESTOCK MUTUAL FUND BUSINESS INSIGHTS")
    print("=" * 70)
    # ============================================================
    # 1. BEST PERFORMING CATEGORIES
    # ============================================================
    print("\n1. BEST PERFORMING CATEGORIES")
    print("-" * 70)
    query = """
    SELECT
        category,
        ROUND(AVG(return_3yr_pct), 2) AS avg_3yr_return
    FROM scheme_performance
    GROUP BY category
    ORDER BY avg_3yr_return DESC;
    """
    for row in conn.execute(query):
        print(row)
    # ============================================================
    # 2. TOP 10 FUNDS BY 3-YEAR RETURN
    # ============================================================
    print("\n2. TOP 10 FUNDS BY 3-YEAR RETURN")
    print("-" * 70)
    query = """
    SELECT
        scheme_name,
        category,
        ROUND(return_3yr_pct, 2) AS return_3yr_pct
    FROM scheme_performance
    ORDER BY return_3yr_pct DESC
    LIMIT 10;
    """
    for row in conn.execute(query):
        print(row)
    # ============================================================
    # 3. FUND HOUSE AUM
    # ============================================================
    print("\n3. FUND HOUSE AUM")
    print("-" * 70)
    query = """
    SELECT
        fund_house,
        ROUND(AVG(aum_crore), 2) AS avg_aum_crore
    FROM aum_by_fund_house
    GROUP BY fund_house
    ORDER BY avg_aum_crore DESC;
    """
    for row in conn.execute(query):
        print(row)
    # ============================================================
    # 4. CATEGORY-WISE NET INFLOW
    # ===========================================================
    print("\n4. CATEGORY-WISE NET INFLOW")
    print("-" * 70)
    query = """
    SELECT
        category,
        ROUND(SUM(net_inflow_crore), 2) AS total_net_inflow_crore
    FROM category_inflows
    GROUP BY category
    ORDER BY total_net_inflow_crore DESC;
    """
    for row in conn.execute(query):
        print(row)
    # ============================================================
    # 5. TRANSACTION TYPE ANALYSIS
    # ============================================================
    print("\n5. TRANSACTION TYPE ANALYSIS")
    print("-" * 70)
    query = """
    SELECT
        transaction_type,
        COUNT(*) AS transaction_count,
        ROUND(AVG(amount_inr), 2) AS average_amount_inr
    FROM investor_transactions
    GROUP BY transaction_type
    ORDER BY transaction_count DESC;
    """
    for row in conn.execute(query):
        print(row)
    # ============================================================
    # CLOSE DATABASE
    # ============================================================
    conn.close()
    print("\n" + "=" * 70)
    print("BUSINESS INSIGHTS ANALYSIS COMPLETE")
    print("=" * 70)
if __name__ == "__main__":
    main()