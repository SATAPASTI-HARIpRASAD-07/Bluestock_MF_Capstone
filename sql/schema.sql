-- Bluestock Mutual Fund Analytics Platform
-- Relational / Star Schema DDL for SQLite Database (db/bluestock_mf.db)

PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. DIMENSION TABLES
-- ============================================================

-- Fund Dimension
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL
);

-- ============================================================
-- 2. FACT TABLES
-- ============================================================

-- NAV History Fact Table
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    date DATE NOT NULL,
    nav REAL NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- Investor Transactions Fact Table
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- Fund Performance Fact Table
CREATE TABLE IF NOT EXISTS fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating REAL,
    anomaly_flag INTEGER DEFAULT 0,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- AUM Fact Table
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER
);

-- Portfolio Holdings Fact Table
CREATE TABLE IF NOT EXISTS fact_portfolio (
    holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    weight_pct REAL NOT NULL,
    market_value_cr REAL NOT NULL,
    current_price_inr REAL,
    portfolio_date DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- Monthly SIP Industry Fact Table
CREATE TABLE IF NOT EXISTS fact_sip_industry (
    sip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE NOT NULL,
    sip_inflow_crore REAL NOT NULL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

-- Category Inflows Fact Table
CREATE TABLE IF NOT EXISTS fact_category_inflows (
    inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE NOT NULL,
    category TEXT NOT NULL,
    net_inflow_crore REAL NOT NULL
);

-- Industry Folio Count Fact Table
CREATE TABLE IF NOT EXISTS fact_industry_folio (
    folio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE NOT NULL,
    total_folios_crore REAL NOT NULL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

-- Benchmark Indices Fact Table
CREATE TABLE IF NOT EXISTS fact_benchmark (
    benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    index_name TEXT NOT NULL,
    close_value REAL NOT NULL
);

-- ============================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_nav_amfi_date ON fact_nav(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_tx_amfi_date ON fact_transactions(amfi_code, transaction_date);
CREATE INDEX IF NOT EXISTS idx_tx_state ON fact_transactions(state);
CREATE INDEX IF NOT EXISTS idx_portfolio_amfi ON fact_portfolio(amfi_code);
CREATE INDEX IF NOT EXISTS idx_benchmark_name_date ON fact_benchmark(index_name, date);
