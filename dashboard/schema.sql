-- Bluestock Mutual Fund Analytics
-- SQLite Star Schema Design
-- Day 2: Data Cleaning + SQL Database Design
PRAGMA foreign_keys = ON;
-- ============================================================
-- 1. FUND DIMENSION
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date DATE,
    benchmark TEXT,
    risk_grade TEXT
);
-- ============================================================
-- 2. DATE DIMENSION
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name TEXT,
    day INTEGER,
    day_of_week INTEGER
);

-- ============================================================
-- 3. NAV FACT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    nav REAL NOT NULL,
    
    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);

-- ============================================================
-- 4. INVESTOR TRANSACTION FACT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount_inr REAL NOT NULL,
    state TEXT,
    kyc_status TEXT,

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);

-- ============================================================
-- 5. FUND PERFORMANCE FACT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    date_key INTEGER,
    return_3yr_pct REAL,
    sharpe_ratio REAL,
    expense_ratio_pct REAL,
    return_anomaly_flag INTEGER DEFAULT 0,
    expense_ratio_anomaly_flag INTEGER DEFAULT 0,
    anomaly_flag INTEGER DEFAULT 0,

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);

-- ============================================================
-- 6. AUM FACT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT NOT NULL,
    date_key INTEGER NOT NULL,
    aum_crore REAL NOT NULL,

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);

-- ============================================================
-- STAR SCHEMA RELATIONSHIPS
-- ============================================================
--
--                 dim_date
--                    |
--                    |
--     dim_fund ----- fact_nav
--        |
--        +---------- fact_transactions
--        |
--        +---------- fact_performance
--
--                 dim_date
--                    |
--                    |
--                fact_aum
--
-- ============================================================