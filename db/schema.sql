-- Bluestock Nifty 100 Financial Intelligence Database Schema

PRAGMA foreign_keys = ON;

-- 1. Companies Table
CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    nse_symbol TEXT NOT NULL,
    bse_code TEXT,
    isin TEXT,
    broad_sector TEXT NOT NULL,
    sub_sector TEXT NOT NULL,
    index_weight_pct REAL DEFAULT 0.0,
    market_cap_category TEXT DEFAULT 'Large Cap'
);

-- 2. Sectors Table
CREATE TABLE IF NOT EXISTS sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    broad_sector TEXT NOT NULL,
    sub_sector TEXT NOT NULL,
    index_weight_pct REAL,
    market_cap_category TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 3. Peer Groups Table
CREATE TABLE IF NOT EXISTS peer_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    peer_group_name TEXT NOT NULL,
    company_id TEXT NOT NULL,
    is_benchmark BOOLEAN DEFAULT 0,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 4. Financial Ratios Table
CREATE TABLE IF NOT EXISTS financial_ratios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    debt_to_equity REAL,
    interest_coverage REAL,
    asset_turnover REAL,
    free_cash_flow_cr REAL,
    capex_cr REAL,
    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,
    total_debt_cr REAL,
    cash_from_operations_cr REAL,
    year_label TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    UNIQUE(company_id, year)
);

-- 5. Market Cap & Valuation Table
CREATE TABLE IF NOT EXISTS market_cap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    market_cap_crore REAL,
    enterprise_value_crore REAL,
    pe_ratio REAL,
    pb_ratio REAL,
    ev_ebitda REAL,
    dividend_yield_pct REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    UNIQUE(company_id, year)
);

-- 6. Stock Prices Table
CREATE TABLE IF NOT EXISTS stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    date TEXT NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,
    adjusted_close REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    UNIQUE(company_id, date)
);

-- 7. Profit & Loss Statement Table (Derived / Reconstructed)
CREATE TABLE IF NOT EXISTS profitandloss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    sales_cr REAL,
    expenses_cr REAL,
    operating_profit_cr REAL,
    opm_pct REAL,
    other_income_cr REAL,
    interest_cr REAL,
    depreciation_cr REAL,
    profit_before_tax_cr REAL,
    tax_pct REAL,
    net_profit_cr REAL,
    npm_pct REAL,
    eps_in_rs REAL,
    dividend_payout_pct REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    UNIQUE(company_id, year)
);

-- 8. Balance Sheet Statement Table (Derived / Reconstructed)
CREATE TABLE IF NOT EXISTS balancesheet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    equity_capital_cr REAL,
    reserves_cr REAL,
    total_equity_cr REAL,
    borrowings_cr REAL,
    other_liabilities_cr REAL,
    total_liabilities_cr REAL,
    fixed_assets_cr REAL,
    cwip_cr REAL,
    investments_cr REAL,
    other_asset_cr REAL,
    total_assets_cr REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    UNIQUE(company_id, year)
);

-- 9. Cash Flow Statement Table (Derived / Reconstructed)
CREATE TABLE IF NOT EXISTS cashflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,
    cash_from_operating_activity_cr REAL,
    cash_from_investing_activity_cr REAL,
    cash_from_financing_activity_cr REAL,
    net_cash_flow_cr REAL,
    capex_cr REAL,
    free_cash_flow_cr REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    UNIQUE(company_id, year)
);

-- 10. Qualitative Analysis Table
CREATE TABLE IF NOT EXISTS analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 11. Pros and Cons Table
CREATE TABLE IF NOT EXISTS prosandcons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    pros TEXT,
    cons TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 12. Documents Repository Table
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    document_type TEXT NOT NULL,
    year TEXT NOT NULL,
    document_title TEXT NOT NULL,
    file_url TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(broad_sector);
CREATE INDEX IF NOT EXISTS idx_ratios_company_year ON financial_ratios(company_id, year);
CREATE INDEX IF NOT EXISTS idx_mcap_company_year ON market_cap(company_id, year);
CREATE INDEX IF NOT EXISTS idx_prices_company_date ON stock_prices(company_id, date);
CREATE INDEX IF NOT EXISTS idx_peer_groups_name ON peer_groups(peer_group_name);
CREATE INDEX IF NOT EXISTS idx_pl_company_year ON profitandloss(company_id, year);
CREATE INDEX IF NOT EXISTS idx_bs_company_year ON balancesheet(company_id, year);
CREATE INDEX IF NOT EXISTS idx_cf_company_year ON cashflow(company_id, year);
