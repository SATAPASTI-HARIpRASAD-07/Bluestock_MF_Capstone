# Bluestock Mutual Fund Analytics
# Data Dictionary

## 1. Fund Master

**File:** `01_fund_master.csv`  
**Rows:** 40  
**Purpose:** Contains master information about mutual fund schemes.

| Column | Data Type | Description |
|---|---|---|
| `amfi_code` | Integer | Unique AMFI identifier for the mutual fund scheme. |
| `fund_house` | String | Name of the mutual fund house. |
| `scheme_name` | String | Full name of the mutual fund scheme. |
| `category` | String | Broad mutual fund category. |
| `sub_category` | String | More specific classification of the fund. |
| `plan` | String | Investment plan such as Regular or Direct. |
| `launch_date` | Date/String | Date on which the scheme was launched. |
| `benchmark` | String | Benchmark index used for performance comparison. |
| `expense_ratio_pct` | Float | Annual expense ratio charged by the fund, in percentage. |
| `exit_load_pct` | Float | Exit load applicable to the scheme, in percentage. |
| `min_sip_amount` | Integer | Minimum amount required for SIP investment. |
| `min_lumpsum_amount` | Integer | Minimum amount required for lumpsum investment. |
| `fund_manager` | String | Name of the fund manager. |
| `risk_category` | String | Risk classification of the scheme. |
| `sebi_category_code` | String | SEBI category classification code. |

---

## 2. NAV History

**File:** `02_nav_history.csv`  
**Rows:** 46,000  
**Purpose:** Contains historical Net Asset Value information for mutual fund schemes.

| Column | Data Type | Description |
|---|---|---|
| `amfi_code` | Integer | AMFI identifier of the mutual fund scheme. |
| `date` | Date/String | Date of the NAV observation. |
| `nav` | Float | Net Asset Value of the mutual fund scheme. |

---

## 3. AUM by Fund House

**File:** `03_aum_by_fund_house.csv`  
**Rows:** 90  
**Purpose:** Tracks Assets Under Management across mutual fund houses.

| Column | Data Type | Description |
|---|---|---|
| `date` | Date/String | Reporting date. |
| `fund_house` | String | Name of the mutual fund house. |
| `aum_lakh_crore` | Float | AUM expressed in lakh crore. |
| `aum_crore` | Integer | AUM expressed in crore rupees. |
| `num_schemes` | Integer | Number of schemes managed by the fund house. |

---

## 4. Monthly SIP Inflows

**File:** `04_monthly_sip_inflows.csv`  
**Rows:** 48  
**Purpose:** Tracks monthly SIP investment activity and growth.

| Column | Data Type | Description |
|---|---|---|
| `month` | String | Month of the observation. |
| `sip_inflow_crore` | Integer | Monthly SIP inflow in crore rupees. |
| `active_sip_accounts_crore` | Float | Number of active SIP accounts expressed in crore. |
| `new_sip_accounts_lakh` | Float | New SIP accounts created, expressed in lakh. |
| `sip_aum_lakh_crore` | Float | SIP-linked AUM expressed in lakh crore. |
| `yoy_growth_pct` | Float | Year-over-year SIP growth percentage. |

**Missing Value Note:**  
The first 12 months have missing `yoy_growth_pct` values because previous-year data is not available for calculating year-over-year growth.

---

## 5. Category Inflows

**File:** `05_category_inflows.csv`  
**Rows:** 144  
**Purpose:** Tracks net mutual fund inflows by category and month.

| Column | Data Type | Description |
|---|---|---|
| `month` | String | Month of the observation. |
| `category` | String | Mutual fund category. |
| `net_inflow_crore` | Float | Net money flowing into the category, in crore rupees. |

---

## 6. Industry Folio Count

**File:** `06_industry_folio_count.csv`  
**Rows:** 21  
**Purpose:** Tracks mutual fund folio counts across major investment segments.

| Column | Data Type | Description |
|---|---|---|
| `month` | String | Month of the observation. |
| `total_folios_crore` | Float | Total mutual fund folios expressed in crore. |
| `equity_folios_crore` | Float | Equity folios expressed in crore. |
| `debt_folios_crore` | Float | Debt folios expressed in crore. |
| `hybrid_folios_crore` | Float | Hybrid fund folios expressed in crore. |
| `others_folios_crore` | Float | Other category folios expressed in crore. |

---

## 7. Scheme Performance

**File:** `07_scheme_performance.csv`  
**Rows:** 40  
**Purpose:** Contains performance, risk, and valuation-related metrics for mutual fund schemes.

| Column | Data Type | Description |
|---|---|---|
| `amfi_code` | Integer | AMFI identifier of the scheme. |
| `scheme_name` | String | Name of the mutual fund scheme. |
| `fund_house` | String | Name of the mutual fund house. |
| `category` | String | Mutual fund category. |
| `plan` | String | Investment plan such as Regular or Direct. |
| `return_1yr_pct` | Float | One-year return percentage. |
| `return_3yr_pct` | Float | Three-year return percentage. |
| `return_5yr_pct` | Float | Five-year return percentage. |
| `benchmark_3yr_pct` | Float | Three-year benchmark return percentage. |
| `alpha` | Float | Excess return relative to the benchmark. |
| `beta` | Float | Sensitivity of fund returns to market movements. |
| `sharpe_ratio` | Float | Risk-adjusted return measure. |
| `sortino_ratio` | Float | Downside-risk-adjusted return measure. |
| `std_dev_ann_pct` | Float | Annualized standard deviation representing return volatility. |
| `max_drawdown_pct` | Float | Maximum observed decline from a peak value, in percentage. |
| `aum_crore` | Integer | Assets Under Management of the scheme in crore rupees. |
| `expense_ratio_pct` | Float | Annual expense ratio in percentage. |
| `morningstar_rating` | Integer | Morningstar rating assigned to the scheme. |
| `risk_grade` | String | Risk classification of the scheme. |

---

## 8. Investor Transactions

**File:** `08_investor_transactions.csv`  
**Rows:** 32,778  
**Purpose:** Contains investor-level mutual fund transaction information.

| Column | Data Type | Description |
|---|---|---|
| `investor_id` | String | Unique identifier for the investor. |
| `transaction_date` | Date/String | Date of the transaction. |
| `amfi_code` | Integer | AMFI identifier of the related fund scheme. |
| `transaction_type` | String | Type of transaction: SIP, Lumpsum, or Redemption. |
| `amount_inr` | Integer | Transaction amount in Indian rupees. |
| `state` | String | State where the investor is located. |
| `city` | String | Investor city. |
| `city_tier` | String | Classification of the city, such as T30 or B30. |
| `age_group` | String | Age group of the investor. |
| `gender` | String | Gender category recorded for the investor. |
| `annual_income_lakh` | Float | Investor annual income in lakh rupees. |
| `payment_mode` | String | Mode used for the transaction. |
| `kyc_status` | String | KYC verification status of the investor. |

---

## 9. Portfolio Holdings

**File:** `09_portfolio_holdings.csv`  
**Rows:** 322  
**Purpose:** Contains individual securities held within mutual fund portfolios.

| Column | Data Type | Description |
|---|---|---|
| `amfi_code` | Integer | AMFI identifier of the mutual fund scheme. |
| `stock_symbol` | String | Stock market symbol of the security. |
| `stock_name` | String | Name of the company/security. |
| `sector` | String | Sector to which the security belongs. |
| `weight_pct` | Float | Percentage weight of the security in the portfolio. |
| `market_value_cr` | Float | Market value of the holding in crore rupees. |
| `current_price_inr` | Float | Current price of the security in Indian rupees. |
| `portfolio_date` | Date/String | Date of the portfolio holding information. |

---

## 10. Benchmark Indices

**File:** `10_benchmark_indices.csv`  
**Rows:** 8,050  
**Purpose:** Contains historical values of benchmark market indices for comparison.

| Column | Data Type | Description |
|---|---|---|
| `date` | Date/String | Date of the index observation. |
| `index_name` | String | Name of the benchmark index. |
| `close_value` | Float | Closing value of the benchmark index. |

---

# Data Quality Summary

| Dataset | Rows | Missing Values |
|---|---:|---|
| Fund Master | 40 | None |
| NAV History | 46,000 | None |
| AUM by Fund House | 90 | None |
| Monthly SIP Inflows | 48 | 12 in `yoy_growth_pct` — Expected |
| Category Inflows | 144 | None |
| Industry Folio Count | 21 | None |
| Scheme Performance | 40 | None |
| Investor Transactions | 32,778 | None |
| Portfolio Holdings | 322 | None |
| Benchmark Indices | 8,050 | None |

---

# Data Sources and Processing

The datasets were supplied as part of the Bluestock Mutual Fund Analytics capstone project.

The data processing workflow is:

1. Raw CSV files are identified.
2. CSV files are loaded using Python and Pandas.
3. Data types are processed and standardized.
4. Duplicate and invalid records are checked.
5. Relevant values are validated.
6. Cleaned datasets are saved in `data/processed/`.
7. Processed datasets are loaded into the SQLite database `bluestock_mf.db`.
8. SQL queries are used for analytical analysis.
9. Results are used for business insights and dashboard visualizations.

# Database Tables

The processed datasets are loaded into the following SQLite tables:

- `fund_master`
- `nav_history`
- `aum_by_fund_house`
- `monthly_sip_inflows`
- `category_inflows`
- `industry_folio_count`
- `scheme_performance`
- `investor_transactions`
- `portfolio_holdings`
- `benchmark_indices`

# File Reference

- `clean_data.py` — Data cleaning and preprocessing
- `inspect_data.py` — Dataset inspection and validation
- `load_to_sql.py` — SQLite database loading
- `sql_analysis.py` — Analytical SQL queries
- `schema.sql` — SQLite star-schema design
- `queries.sql` — Analytical SQL query collection