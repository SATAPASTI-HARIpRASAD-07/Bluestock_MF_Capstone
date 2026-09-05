-- Bluestock Mutual Fund Capstone
-- Day 2: Analytical SQL Queries
-- =========================================================
-- QUERY 1: Top 5 Funds by AUM
-- =========================================================
SELECT
    fund_house,
    ROUND(MAX(aum_crore), 2) AS latest_aum_crore
FROM aum_by_fund_house
GROUP BY fund_house
ORDER BY latest_aum_crore DESC
LIMIT 5;
-- =========================================================
-- QUERY 2: Average NAV per Month
-- =========================================================
SELECT
    strftime('%Y-%m', date) AS month,
    ROUND(AVG(nav), 2) AS average_nav
FROM nav_history
GROUP BY strftime('%Y-%m', date)
ORDER BY month;
-- =========================================================
-- QUERY 3: SIP YoY Growth
-- =========================================================
SELECT
    month,
    sip_inflow_crore,
    yoy_growth_pct
FROM monthly_sip_inflows
ORDER BY month;
-- =========================================================
-- QUERY 4: Transactions by State
-- =========================================================

SELECT
    state,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_transaction_amount
FROM investor_transactions
GROUP BY state
ORDER BY total_transaction_amount DESC;


-- =========================================================
-- QUERY 5: Funds with Expense Ratio < 1%
-- =========================================================

SELECT
    scheme_name,
    category,
    expense_ratio_pct,
    return_3yr_pct
FROM scheme_performance
WHERE expense_ratio_pct < 1
ORDER BY expense_ratio_pct ASC;


-- =========================================================
-- QUERY 6: Top 10 Funds by 3-Year Return
-- =========================================================

SELECT
    scheme_name,
    category,
    ROUND(return_3yr_pct, 2) AS return_3yr_pct
FROM scheme_performance
ORDER BY return_3yr_pct DESC
LIMIT 10;


-- =========================================================
-- QUERY 7: Average Return by Category
-- =========================================================

SELECT
    category,
    ROUND(AVG(return_3yr_pct), 2) AS average_3yr_return
FROM scheme_performance
GROUP BY category
ORDER BY average_3yr_return DESC;


-- =========================================================
-- QUERY 8: Transaction Type Analysis
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
-- QUERY 9: Fund House AUM Analysis
-- =========================================================

SELECT
    fund_house,
    ROUND(AVG(aum_crore), 2) AS average_aum_crore,
    ROUND(MAX(aum_crore), 2) AS maximum_aum_crore
FROM aum_by_fund_house
GROUP BY fund_house
ORDER BY average_aum_crore DESC;


-- =========================================================
-- QUERY 10: Sector Exposure
-- =========================================================

SELECT
    sector,
    COUNT(*) AS number_of_holdings,
    ROUND(AVG(weight_pct), 2) AS average_weight_pct,
    ROUND(AVG(market_value_cr), 2) AS average_market_value_cr
FROM portfolio_holdings
GROUP BY sector
ORDER BY average_weight_pct DESC;