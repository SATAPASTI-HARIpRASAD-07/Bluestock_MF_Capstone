# BLUESTOCK FINTECH — MUTUAL FUND ANALYTICS
## Power BI / Tableau 4-Page Dashboard Specification

This document provides complete visual, data model, measure mapping, and UI layout specifications for building the 4-page Bluestock Mutual Fund Analytics Dashboard in Power BI Desktop or Tableau.

---

## 🎨 Theme & Styling Standards
- **Primary Color**: `#1E3A8A` (Dark Navy Blue)
- **Secondary Accent**: `#4F46E5` (Indigo Accent)
- **Positive Metric / Success**: `#10B981` (Emerald Green)
- **Alert / Warning**: `#EF4444` (Crimson Red)
- **Canvas Dimensions**: 16:9 Widescreen (`1280 x 720` px or `1920 x 1080` px)
- **Font Family**: Segoe UI / Arial Clean

---

## 📄 Page 1 — Industry Overview

### Objective
Provide macro-level mutual fund industry metrics, total AUM growth trends, monthly SIP inflows, total folios, and fund house rankings.

### Visual Components & Layout
1. **KPI Header Banner (Top Cards)**:
   - **Card 1**: `[Total AUM Cr]` — Title: *Total Industry AUM (Cr)*
   - **Card 2**: `[Latest Monthly SIP Inflow Cr]` — Title: *Monthly SIP Inflow (Cr)*
   - **Card 3**: `[Total Folio Count Cr]` — Title: *Total Industry Folios (Cr)*
   - **Card 4**: `[Active Schemes Count]` — Title: *Active Schemes Analyzed*
2. **Chart 1 (Middle Left - Line Chart)**:
   - **Visual**: Line Chart
   - **X-Axis**: `fact_aum[date]` (Year/Month Hierarchy)
   - **Y-Axis**: `[Industry AUM Trajectory Cr]`
   - **Title**: *Industry AUM Growth Trajectory (INR Crore)*
3. **Chart 2 (Middle Right - Horizontal Bar Chart)**:
   - **Visual**: Clustered Bar Chart
   - **Y-Axis**: `fact_aum[fund_house]`
   - **X-Axis**: `[Total AUM Cr]` (Sort Descending, Top 10 Filter)
   - **Title**: *Top 10 Fund Houses by Total AUM (INR Crore)*
4. **Chart 3 (Bottom Left - Stacked Area Chart)**:
   - **Visual**: Stacked Area Chart
   - **X-Axis**: `fact_industry_folio[month]`
   - **Values**: `equity_folios_crore`, `debt_folios_crore`, `hybrid_folios_crore`, `others_folios_crore`
   - **Title**: *Industry Folio Count Breakdown by Asset Segment*

---

## 📄 Page 2 — Fund Performance & Scorecard

### Objective
Analyze risk-adjusted fund returns, Volatility vs Return trade-offs, composite scorecard rankings, and individual scheme NAV trajectories vs benchmarks.

### Slicers & Global Filters (Top Bar / Left Panel)
- **Slicer 1 (Dropdown)**: `dim_fund[fund_house]` (*Fund House Slicer*)
- **Slicer 2 (Dropdown)**: `dim_fund[category]` (*Category Slicer*)
- **Slicer 3 (Tile / Buttons)**: `dim_fund[plan]` (*Direct / Regular Plan Slicer*)
- **Slicer 4 (Date Slider)**: `dim_date[full_date]` (*Date Range Filter*)

### Visual Components & Layout
1. **Visual 1 (Top Left - Scatter Plot)**:
   - **Visual**: Scatter Chart
   - **X-Axis**: `fact_performance[std_dev_ann_pct]` (*Annualized Volatility / Risk %*)
   - **Y-Axis**: `fact_performance[return_3yr_pct]` (*3-Year CAGR Return %*)
   - **Details / Tooltips**: `dim_fund[scheme_name]`, `[Avg Sharpe Ratio]`, `[Avg Alpha]`
   - **Legend**: `dim_fund[category]`
   - **Title**: *Risk (Annualized Volatility %) vs Return (3-Year CAGR %)*
2. **Visual 2 (Top Right - Grouped Bar Chart)**:
   - **Visual**: Clustered Column Chart
   - **X-Axis**: `dim_fund[scheme_name]` (Top 10 Filter)
   - **Y-Axis**: `[Avg 3Yr CAGR Return %]` vs `[Benchmark 3Yr Return %]`
   - **Title**: *Fund Return vs Benchmark Return (Top 10 Schemes)*
3. **Visual 3 (Bottom Table - Composite Scorecard Grid)**:
   - **Visual**: Table / Matrix with Conditional Formatting
   - **Columns**: `rank`, `scheme_name`, `category`, `fund_house`, `plan`, `return_3yr_pct`, `sharpe_ratio`, `alpha`, `beta`, `expense_ratio_pct`, `max_drawdown_pct`, `composite_score`
   - **Sort**: `rank` Ascending (or `composite_score` Descending)
   - **Conditional Formatting**: Background Color gradient on `composite_score` (Green to White)
   - **Title**: *Composite Mutual Fund Scorecard & Metrics Table*
4. **Visual 4 (Bottom Right - Line Chart)**:
   - **Visual**: Line Chart
   - **X-Axis**: `fact_nav[date]`
   - **Y-Axis**: `[Selected Fund NAV]`
   - **Legend / Filter**: `dim_fund[scheme_name]`
   - **Title**: *Selected Scheme NAV Performance Trajectory*

---

## 📄 Page 3 — Investor Analytics

### Objective
Examine investor transaction behaviors, geographic state-wise volumes, transaction type splits (SIP vs Lumpsum vs Redemption), age group demographics, and city tier participation.

### Slicers & Global Filters
- **Slicer 1 (Dropdown)**: `fact_transactions[state]` (*State Filter*)
- **Slicer 2 (Dropdown)**: `fact_transactions[age_group]` (*Age Group Filter*)
- **Slicer 3 (Buttons)**: `fact_transactions[city_tier]` (*T30 vs B30 City Tier Filter*)

### Visual Components & Layout
1. **KPI Header Banner (Top Cards)**:
   - **Card 1**: `[Total Investor Transactions]` — Title: *Total Transactions*
   - **Card 2**: `[Total Investment Volume Cr]` — Title: *Total Investment Volume (Cr)*
   - **Card 3**: `[SIP Volume Cr]` — Title: *SIP Volume (Cr)*
   - **Card 4**: `[Redemption Volume Cr]` — Title: *Redemption Volume (Cr)*
2. **Chart 1 (Middle Left - Horizontal Bar Chart)**:
   - **Visual**: Clustered Bar Chart
   - **Y-Axis**: `fact_transactions[state]` (Top 10 States Filter)
   - **X-Axis**: `[Total Investment Volume Cr]`
   - **Title**: *Top 10 States by Total Investor Transaction Volume (Cr)*
3. **Chart 2 (Middle Right - Donut / Pie Chart)**:
   - **Visual**: Donut Chart
   - **Legend**: `fact_transactions[transaction_type]` (SIP, Lumpsum, Redemption)
   - **Values**: `[Total Investment Volume Cr]`
   - **Title**: *Transaction Type Breakdown (Volume Split)*
4. **Chart 3 (Bottom Left - Column Chart)**:
   - **Visual**: Clustered Column Chart
   - **X-Axis**: `fact_transactions[age_group]`
   - **Y-Axis**: `[Total Investment Volume Cr]` and `[Avg Transaction Amount INR]` (Line on secondary Y-axis)
   - **Title**: *Investment Volume & Average Amount by Age Group*
5. **Chart 4 (Bottom Right - Area Chart)**:
   - **Visual**: Area Chart
   - **X-Axis**: `fact_transactions[transaction_date]` (Monthly Grouping)
   - **Values**: `[SIP Transaction Count]`, `[Lumpsum Transaction Count]`, `[Redemption Transaction Count]`
   - **Title**: *Monthly Transaction Count Trajectory by Type*

---

## 📄 Page 4 — SIP & Market Trends

### Objective
Track long-term industry SIP growth, active/new account registrations, benchmark index market performance (Nifty 50, Nifty 100), and category net inflows.

### Visual Components & Layout
1. **KPI Header Banner (Top Cards)**:
   - **Card 1**: `[Latest Monthly SIP Inflow Cr]` — Title: *Monthly SIP Inflow (Cr)*
   - **Card 2**: `[Active SIP Accounts Cr]` — Title: *Active SIP Accounts (Cr)*
   - **Card 3**: `[New SIP Accounts Lakh]` — Title: *New Monthly SIP Accounts (Lakh)*
   - **Card 4**: `[Total Category Net Inflow Cr]` — Title: *Total Category Net Inflow (Cr)*
2. **Chart 1 (Top Left - Line Chart)**:
   - **Visual**: Line Chart
   - **X-Axis**: `fact_sip_industry[month]`
   - **Y-Axis**: `fact_sip_industry[sip_inflow_crore]`
   - **Title**: *Monthly Industry SIP Inflow Trajectory (INR Crore)*
3. **Chart 2 (Top Right - Line Chart)**:
   - **Visual**: Line Chart
   - **X-Axis**: `fact_benchmark[date]`
   - **Y-Axis**: `fact_benchmark[close_value]`
   - **Legend**: `fact_benchmark[index_name]` (NIFTY50, NIFTY100, NIFTY MIDCAP 150, BSE SMALLCAP)
   - **Title**: *Benchmark Market Indices Performance Trajectory*
4. **Chart 3 (Bottom Left - Matrix / Heatmap)**:
   - **Visual**: Matrix with Conditional Color Formatting
   - **Rows**: `fact_category_inflows[category]`
   - **Columns**: `fact_category_inflows[month]`
   - **Values**: `[Total Category Net Inflow Cr]`
   - **Title**: *Category-Wise Net Monthly Inflow Heatmap (INR Crore)*
5. **Chart 4 (Bottom Right - Bar Chart)**:
   - **Visual**: Clustered Bar Chart
   - **Y-Axis**: `fact_category_inflows[category]` (Top 5 Filter)
   - **X-Axis**: `[Total Category Net Inflow Cr]`
   - **Title**: *Top 5 Mutual Fund Categories by Total Net Inflow (Cr)*
