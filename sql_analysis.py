import sqlite3
DB_FILE = "bluestock_mf.db"
conn = sqlite3.connect(DB_FILE)
print("=" * 70)
print("BLUESTOCK MUTUAL FUND SQL ANALYSIS")
print("=" * 70)
# ============================================================
# 1. FUND PERFORMANCE BY CATEGORY
# ============================================================
print("\n1. FUND PERFORMANCE BY CATEGORY")
print("-" * 70)
query = """
SELECT
    category,
    COUNT(*) AS number_of_schemes,
    ROUND(AVG(return_1yr_pct), 2) AS avg_1yr_return,
    ROUND(AVG(return_3yr_pct), 2) AS avg_3yr_return,
    ROUND(AVG(return_5yr_pct), 2) AS avg_5yr_return
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
    plan,
    return_3yr_pct
FROM scheme_performance
ORDER BY return_3yr_pct DESC
LIMIT 10;
"""
for row in conn.execute(query):
    print(row)
# ============================================================
# 3. TOP FUNDS BY SHARPE RATIO
# ============================================================
print("\n3. TOP 10 FUNDS BY SHARPE RATIO")
print("-" * 70)
query = """
SELECT
    scheme_name,
    category,
    sharpe_ratio,
    risk_grade
FROM scheme_performance
ORDER BY sharpe_ratio DESC
LIMIT 10;
"""
for row in conn.execute(query):
    print(row)
# ============================================================
# 4. FUND HOUSE AUM
# ============================================================
print("\n4. FUND HOUSE AUM")
print("-" * 70)
query = """
SELECT
    fund_house,
    ROUND(AVG(aum_crore), 2) AS average_aum_crore,
    MAX(aum_crore) AS maximum_aum_crore
FROM scheme_performance
GROUP BY fund_house
ORDER BY average_aum_crore DESC;
"""
for row in conn.execute(query):
    print(row)
# ============================================================
# 5. SIP INFLOW TREND
# ============================================================
print("\n5. SIP INFLOW TREND")
print("-" * 70)
query = """
SELECT
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    sip_aum_lakh_crore
FROM monthly_sip_inflows
ORDER BY month;
"""
for row in conn.execute(query):
    print(row)
# ============================================================
# 6. CATEGORY-WISE NET INFLOW
# ============================================================
print("\n6. CATEGORY-WISE NET INFLOW")
print("-" * 70)
query = """
SELECT
    category,
    ROUND(SUM(net_inflow_crore), 2) AS total_net_inflow
FROM category_inflows
GROUP BY category
ORDER BY total_net_inflow DESC;
"""
for row in conn.execute(query):
    print(row)
# ============================================================
# 7. TRANSACTION TYPE ANALYSIS
# ============================================================
print("\n7. TRANSACTION TYPE ANALYSIS")
print("-" * 70)
query = """
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS average_amount_inr
FROM investor_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;
"""
for row in conn.execute(query):
    print(row)
# ============================================================
# 8. STATE-WISE INVESTOR TRANSACTIONS
# ============================================================
print("\n8. STATE-WISE INVESTOR TRANSACTIONS")
print("-" * 70)
query = """
SELECT
    state,
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_amount_inr
FROM investor_transactions
GROUP BY state
ORDER BY total_amount_inr DESC
LIMIT 10;
"""
for row in conn.execute(query):
    print(row)
# ============================================================
# 9. AVERAGE PORTFOLIO SECTOR EXPOSURE
# ============================================================
print("\n9. AVERAGE PORTFOLIO SECTOR EXPOSURE")
print("-" * 70)
query = """
SELECT
    sector,
    COUNT(*) AS number_of_holdings,
    ROUND(AVG(weight_pct), 2) AS avg_weight_pct,
    ROUND(AVG(market_value_cr), 2) AS avg_market_value_cr
FROM portfolio_holdings
GROUP BY sector
ORDER BY avg_weight_pct DESC;
"""
for row in conn.execute(query):
    print(row)
# ============================================================
# 10. BENCHMARK INDEX SUMMARY
# ============================================================
print("\n10. BENCHMARK INDEX SUMMARY")
print("-" * 70)
query = """
SELECT
    index_name,
    COUNT(*) AS number_of_records,
    ROUND(MIN(close_value), 2) AS minimum_value,
    ROUND(MAX(close_value), 2) AS maximum_value,
    ROUND(AVG(close_value), 2) AS average_value
FROM benchmark_indices
GROUP BY index_name
ORDER BY average_value DESC;
"""
for row in conn.execute(query):
    print(row)
# ============================================================
# FINAL
# ============================================================
conn.close()
print("\n" + "=" * 70)
print("SQL BUSINESS ANALYSIS COMPLETE")
print("=" * 70)