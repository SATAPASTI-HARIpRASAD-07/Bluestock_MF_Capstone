# Bluestock Mutual Fund Analytics Platform — Data Dictionary

## 1. Fund Master (`01_fund_master.csv`)
**Rows:** 40 | **Primary Key:** `amfi_code` | **Table:** `dim_fund` / `fund_master`

| Column | Data Type | Description |
|---|---|---|
| `amfi_code` | Integer | Unique Association of Mutual Funds in India (AMFI) scheme identifier. |
| `fund_house` | String | Asset Management Company (AMC) name. |
| `scheme_name` | String | Full legal scheme title. |
| `category` | String | Broad scheme category (Equity, Debt, Hybrid, Solution, Others). |
| `sub_category` | String | SEBI sub-category classification (Large Cap, Small Cap, Mid Cap, Liquid, etc.). |
| `plan` | String | Investment plan tier (Regular, Direct). |
| `launch_date` | Date | Scheme inception date (YYYY-MM-DD). |
| `benchmark` | String | Primary benchmark index identifier. |
| `expense_ratio_pct` | Float | Annual scheme expense ratio percentage. |
| `exit_load_pct` | Float | Applicable exit load percentage. |
| `min_sip_amount` | Integer | Minimum monthly Systematic Investment Plan (SIP) amount in INR. |
| `min_lumpsum_amount` | Integer | Minimum one-time lumpsum investment amount in INR. |
| `fund_manager` | String | Primary designated fund manager. |
| `risk_category` | String | SEBI Riskometer risk grade (Low, Moderate, High, Very High). |
| `sebi_category_code` | String | Standardized SEBI category code (e.g. EC01). |

---

## 2. NAV History (`02_nav_history.csv`)
**Rows:** 46,000 | **Foreign Key:** `amfi_code` | **Table:** `fact_nav` / `nav_history`

| Column | Data Type | Description |
|---|---|---|
| `amfi_code` | Integer | Scheme AMFI identifier. |
| `date` | Date | NAV observation date (YYYY-MM-DD). |
| `nav` | Float | Net Asset Value per unit in INR. |

---

## 3. AUM by Fund House (`03_aum_by_fund_house.csv`)
**Rows:** 90 | **Table:** `fact_aum` / `aum_by_fund_house`

| Column | Data Type | Description |
|---|---|---|
| `date` | Date | Reporting observation date. |
| `fund_house` | String | AMC name. |
| `aum_lakh_crore` | Float | Total Assets Under Management in Lakh Crore INR. |
| `aum_crore` | Float | Total Assets Under Management in Crore INR. |
| `num_schemes` | Integer | Number of active schemes managed. |

---

## 4. Monthly SIP Inflows (`04_monthly_sip_inflows.csv`)
**Rows:** 48 | **Table:** `fact_sip_industry` / `monthly_sip_inflows`

| Column | Data Type | Description |
|---|---|---|
| `month` | Date | Reporting month (YYYY-MM-01). |
| `sip_inflow_crore` | Float | Total monthly SIP inflow volume in Crore INR. |
| `active_sip_accounts_crore` | Float | Total active registered SIP accounts in Crore. |
| `new_sip_accounts_lakh` | Float | New monthly SIP registrations in Lakh. |
| `sip_aum_lakh_crore` | Float | Cumulative SIP-linked AUM in Lakh Crore INR. |
| `yoy_growth_pct` | Float | Year-over-Year SIP growth percentage (12-month lag). |

---

## 5. Category Inflows (`05_category_inflows.csv`)
**Rows:** 144 | **Table:** `fact_category_inflows` / `category_inflows`

| Column | Data Type | Description |
|---|---|---|
| `month` | Date | Reporting month. |
| `category` | String | Mutual fund scheme category. |
| `net_inflow_crore` | Float | Net category inflow (subscriptions minus redemptions) in Crore INR. |

---

## 6. Industry Folio Count (`06_industry_folio_count.csv`)
**Rows:** 21 | **Table:** `fact_industry_folio` / `industry_folio_count`

| Column | Data Type | Description |
|---|---|---|
| `month` | Date | Reporting month. |
| `total_folios_crore` | Float | Total industry investor folios in Crore. |
| `equity_folios_crore` | Float | Equity scheme folios in Crore. |
| `debt_folios_crore` | Float | Debt scheme folios in Crore. |
| `hybrid_folios_crore` | Float | Hybrid scheme folios in Crore. |
| `others_folios_crore` | Float | Solution and ETF folios in Crore. |

---

## 7. Scheme Performance (`07_scheme_performance.csv`)
**Rows:** 40 | **Foreign Key:** `amfi_code` | **Table:** `fact_performance` / `scheme_performance`

| Column | Data Type | Description |
|---|---|---|
| `amfi_code` | Integer | Scheme AMFI identifier. |
| `scheme_name` | String | Scheme name. |
| `fund_house` | String | AMC name. |
| `category` | String | Scheme category. |
| `plan` | String | Plan type (Regular, Direct). |
| `return_1yr_pct` | Float | 1-Year absolute return percentage. |
| `return_3yr_pct` | Float | 3-Year Compound Annual Growth Rate (CAGR) %. |
| `return_5yr_pct` | Float | 5-Year Compound Annual Growth Rate (CAGR) %. |
| `benchmark_3yr_pct` | Float | Benchmark index 3-year return %. |
| `alpha` | Float | Excess return relative to benchmark index (Jensen's Alpha). |
| `beta` | Float | Sensitivity metric relative to benchmark movements. |
| `sharpe_ratio` | Float | Risk-adjusted return ratio ((Rp - Rf) / StdDev). |
| `sortino_ratio` | Float | Downside-risk-adjusted return ratio. |
| `std_dev_ann_pct` | Float | Annualized volatility / standard deviation %. |
| `max_drawdown_pct` | Float | Maximum historical peak-to-trough decline %. |
| `aum_crore` | Float | Scheme AUM in Crore INR. |
| `expense_ratio_pct` | Float | Scheme annual expense ratio %. |
| `morningstar_rating` | Integer | Scheme rating (1 to 5 stars). |
| `anomaly_flag` | Integer | Data anomaly flag (0 = Normal, 1 = Flagged). |

---

## 8. Investor Transactions (`08_investor_transactions.csv`)
**Rows:** 32,778 | **Foreign Key:** `amfi_code` | **Table:** `fact_transactions` / `investor_transactions`

| Column | Data Type | Description |
|---|---|---|
| `investor_id` | String | Unique anonymized investor identifier. |
| `transaction_date` | Date | Date of transaction. |
| `amfi_code` | Integer | Target scheme AMFI identifier. |
| `transaction_type` | String | Transaction category: `SIP`, `Lumpsum`, or `Redemption`. |
| `amount_inr` | Float | Transaction monetary value in INR. |
| `state` | String | Investor residence state. |
| `city` | String | Investor residence city. |
| `city_tier` | String | Location tier classification (`T30` or `B30`). |
| `age_group` | String | Demographic age bracket (`18-25`, `26-35`, `36-45`, `46-55`, `56+`). |
| `gender` | String | Recorded gender identity. |
| `annual_income_lakh` | Float | Self-reported annual income in Lakh INR. |
| `payment_mode` | String | Transaction payment channel (`UPI`, `NetBanking`, `Mandate`, `Cheque`). |
| `kyc_status` | String | Investor KYC verification status (`Verified`, `Pending`, `Rejected`). |

---

## 9. Portfolio Holdings (`09_portfolio_holdings.csv`)
**Rows:** 322 | **Foreign Key:** `amfi_code` | **Table:** `fact_portfolio` / `portfolio_holdings`

| Column | Data Type | Description |
|---|---|---|
| `amfi_code` | Integer | Scheme AMFI identifier. |
| `stock_symbol` | String | NSE/BSE stock ticker symbol. |
| `stock_name` | String | Full corporate issuer name. |
| `sector` | String | Industry sector classification. |
| `weight_pct` | Float | Portfolio weight percentage allocation. |
| `market_value_cr` | Float | Holding market value in Crore INR. |
| `current_price_inr` | Float | Security price per share in INR. |
| `portfolio_date` | Date | Portfolio holding reporting date. |

---

## 10. Benchmark Indices (`10_benchmark_indices.csv`)
**Rows:** 8,050 | **Table:** `fact_benchmark` / `benchmark_indices`

| Column | Data Type | Description |
|---|---|---|
| `date` | Date | Observation date. |
| `index_name` | String | Benchmark index name (Nifty 50, Nifty 100, Nifty Midcap 150, BSE SmallCap, CRISIL Liquid, CRISIL Gilt). |
| `close_value` | Float | Daily closing value of index. |
