-- Bluestock Mutual Fund Analytics Platform
-- Day 2: Analytical SQL Queries Collection (sql/queries.sql)

-- =========================================================
-- QUERY 1: Top 5 Fund Houses by Average AUM
-- =========================================================
SELECT
    fund_house,
    ROUND(AVG(aum_crore), 2) AS avg_aum_crore,
    ROUND(MAX(aum_crore), 2) AS max_aum_crore
FROM aum_by_fund_house
GROUP BY fund_house
ORDER BY avg_aum_crore DESC
LIMIT 5;

-- =========================================================
-- QUERY 2: Average Monthly NAV Trajectory
-- =========================================================
SELECT
    strftime('%Y-%m', date) AS month,
    ROUND(AVG(nav), 2) AS average_nav,
    ROUND(MIN(nav), 2) AS min_nav,
    ROUND(MAX(nav), 2) AS max_nav
FROM nav_history
GROUP BY strftime('%Y-%m', date)
ORDER BY month;

-- =========================================================
-- QUERY 3: Monthly SIP Inflow YoY Growth Analysis
-- =========================================================
SELECT
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    ROUND(yoy_growth_pct, 2) AS yoy_growth_pct
FROM monthly_sip_inflows
WHERE yoy_growth_pct IS NOT NULL
ORDER BY month DESC;

-- =========================================================
-- QUERY 4: Investor Transaction Analysis by State
-- =========================================================
SELECT
    state,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_investment_inr,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_inr
FROM investor_transactions
GROUP BY state
ORDER BY total_investment_inr DESC;

-- =========================================================
-- QUERY 5: Top Low-Cost Performing Funds (Expense Ratio < 1%)
-- =========================================================
SELECT
    scheme_name,
    category,
    expense_ratio_pct,
    return_3yr_pct,
    sharpe_ratio
FROM scheme_performance
WHERE expense_ratio_pct < 1.0
ORDER BY return_3yr_pct DESC;

-- =========================================================
-- QUERY 6: Top 10 Funds by 3-Year CAGR Return
-- =========================================================
SELECT
    scheme_name,
    category,
    fund_house,
    return_3yr_pct
FROM scheme_performance
ORDER BY return_3yr_pct DESC
LIMIT 10;

-- =========================================================
-- QUERY 7: Category Performance & Risk Breakdown
-- =========================================================
SELECT
    category,
    COUNT(*) AS scheme_count,
    ROUND(AVG(return_1yr_pct), 2) AS avg_1yr_return,
    ROUND(AVG(return_3yr_pct), 2) AS avg_3yr_return,
    ROUND(AVG(return_5yr_pct), 2) AS avg_5yr_return,
    ROUND(AVG(sharpe_ratio), 2) AS avg_sharpe_ratio
FROM scheme_performance
GROUP BY category
ORDER BY avg_3yr_return DESC;

-- =========================================================
-- QUERY 8: Transaction Breakdown by Type (SIP vs Lumpsum vs Redemption)
-- =========================================================
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS average_amount_inr
FROM investor_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;

-- =========================================================
-- QUERY 9: Fund Alpha vs Benchmark Alpha Comparison
-- =========================================================
SELECT
    scheme_name,
    category,
    return_3yr_pct,
    benchmark_3yr_pct,
    ROUND(return_3yr_pct - benchmark_3yr_pct, 2) AS excess_return_pct,
    alpha,
    beta
FROM scheme_performance
ORDER BY excess_return_pct DESC;

-- =========================================================
-- QUERY 10: Highest-Risk Funds by Volatility & Max Drawdown
-- =========================================================
SELECT
    scheme_name,
    category,
    risk_grade,
    std_dev_ann_pct,
    max_drawdown_pct,
    sharpe_ratio
FROM scheme_performance
ORDER BY std_dev_ann_pct DESC
LIMIT 10;

-- =========================================================
-- QUERY 11: Sector Concentration Analysis from Portfolio Holdings
-- =========================================================
SELECT
    sector,
    COUNT(DISTINCT stock_symbol) AS distinct_stocks,
    ROUND(AVG(weight_pct), 2) AS avg_weight_pct,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr
FROM portfolio_holdings
GROUP BY sector
ORDER BY avg_weight_pct DESC;

-- =========================================================
-- QUERY 12: State-wise Investment Breakdown by City Tier (T30 vs B30)
-- =========================================================
SELECT
    state,
    city_tier,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM investor_transactions
GROUP BY state, city_tier
ORDER BY total_amount_inr DESC;
