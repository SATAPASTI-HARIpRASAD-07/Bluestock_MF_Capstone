# BLUESTOCK FINTECH — MUTUAL FUND ANALYTICS
## Power BI Desktop Step-by-Step Implementation Guide

This guide provides an exact, step-by-step walkthrough for opening Power BI Desktop, ingesting the prepared data models, configuring relationships, creating DAX measures, building all 4 dashboard pages, and saving `dashboard/bluestock_mf.pbix`.

---

## 🛠️ Step 1: Open Power BI Desktop & Ingest Data

1. Open **Power BI Desktop** on your computer.
2. Click **Get Data** ➔ **Folder** (or **Text/CSV**).
3. Browse to your project folder:
   `c:\Users\HARI PRASAD\Bluestock_MF_Capstone\dashboard\data\`
4. Select and import the following 11 CSV datasets:
   - `dim_fund.csv`
   - `dim_date.csv`
   - `fact_nav.csv`
   - `fact_transactions.csv`
   - `fact_performance.csv`
   - `fact_aum.csv`
   - `fact_portfolio.csv`
   - `fact_sip_industry.csv`
   - `fact_category_inflows.csv`
   - `fact_industry_folio.csv`
   - `fact_benchmark.csv`
5. Click **Load** (or **Transform Data** if you wish to verify column data types).

---

## 🔗 Step 2: Establish Star Schema Relationships

Navigate to **Model View** (left sidebar icon) and create the following relationships:

1. **`dim_fund` ➔ `fact_nav`**:
   - `dim_fund[amfi_code]` (1) ➔ `fact_nav[amfi_code]` (N)
   - Cross filter direction: *Single*

2. **`dim_fund` ➔ `fact_transactions`**:
   - `dim_fund[amfi_code]` (1) ➔ `fact_transactions[amfi_code]` (N)

3. **`dim_fund` ➔ `fact_performance`**:
   - `dim_fund[amfi_code]` (1) ➔ `fact_performance[amfi_code]` (1 or N)

4. **`dim_fund` ➔ `fact_portfolio`**:
   - `dim_fund[amfi_code]` (1) ➔ `fact_portfolio[amfi_code]` (N)

5. **`dim_date` ➔ `fact_nav`**:
   - `dim_date[full_date]` (1) ➔ `fact_nav[date]` (N)

6. **`dim_date` ➔ `fact_transactions`**:
   - `dim_date[full_date]` (1) ➔ `fact_transactions[transaction_date]` (N)

---

## 📐 Step 3: Create DAX Measures Table

1. In **Home** tab, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.
3. Right-click `_Measures` ➔ **New Measure**.
4. Open the provided `dashboard/dax_measures.dax` file and copy-paste the DAX formulas into Power BI Desktop:
   - `Total AUM Cr`
   - `Latest Monthly SIP Inflow Cr`
   - `Total Folio Count Cr`
   - `Active Schemes Count`
   - `Avg 3Yr CAGR Return %`
   - `Avg Sharpe Ratio`
   - `Avg Alpha`
   - `Avg Beta`
   - `Total Investor Transactions`
   - `Total Investment Volume Cr`
   - `SIP Volume Cr`
   - `Redemption Volume Cr`
   - *(Copy remaining measures from `dashboard/dax_measures.dax`)*

---

## 📊 Step 4: Build Dashboard Pages

### Page 1: Industry Overview
1. Rename Page 1 to **`Industry Overview`**.
2. Add 4 **Card Visuals** at the top:
   - Card 1: `_Measures[Total AUM Cr]`
   - Card 2: `_Measures[Latest Monthly SIP Inflow Cr]`
   - Card 3: `_Measures[Total Folio Count Cr]`
   - Card 4: `_Measures[Active Schemes Count]`
3. Add a **Line Chart** for AUM Trajectory:
   - X-Axis: `fact_aum[date]`
   - Y-Axis: `fact_aum[aum_crore]`
4. Add a **Horizontal Bar Chart** for Top 10 Fund Houses:
   - Y-Axis: `fact_aum[fund_house]`
   - X-Axis: `fact_aum[aum_crore]` (Top 10 Filter)

---

### Page 2: Fund Performance & Scorecard
1. Create Page 2 and rename to **`Fund Performance`**.
2. Add Slicers at top: `dim_fund[fund_house]`, `dim_fund[category]`, `dim_fund[plan]`.
3. Add **Scatter Chart**:
   - X-Axis: `fact_performance[std_dev_ann_pct]`
   - Y-Axis: `fact_performance[return_3yr_pct]`
   - Legend: `dim_fund[category]`
4. Add **Table Visual** for Scorecard:
   - Drag `rank`, `scheme_name`, `category`, `return_3yr_pct`, `sharpe_ratio`, `alpha`, `composite_score`.
   - Apply Conditional Formatting gradient on `composite_score`.

---

### Page 3: Investor Analytics
1. Create Page 3 and rename to **`Investor Analytics`**.
2. Add Slicers: `fact_transactions[state]`, `fact_transactions[age_group]`, `fact_transactions[city_tier]`.
3. Add **Bar Chart**: Y-Axis = `state`, X-Axis = `[Total Investment Volume Cr]`.
4. Add **Donut Chart**: Legend = `transaction_type`, Values = `[Total Investment Volume Cr]`.
5. Add **Column Chart**: X-Axis = `age_group`, Y-Axis = `[Total Investment Volume Cr]`.

---

### Page 4: SIP & Market Trends
1. Create Page 4 and rename to **`SIP & Market Trends`**.
2. Add **Line Chart**: X-Axis = `fact_sip_industry[month]`, Y-Axis = `fact_sip_industry[sip_inflow_crore]`.
3. Add **Line Chart**: X-Axis = `fact_benchmark[date]`, Y-Axis = `fact_benchmark[close_value]`, Legend = `index_name`.
4. Add **Matrix Heatmap**: Rows = `category`, Columns = `month`, Values = `net_inflow_crore`.

---

## 💾 Step 5: Save Project File

1. Click **File** ➔ **Save As**.
2. Browse to `c:\Users\HARI PRASAD\Bluestock_MF_Capstone\dashboard\`.
3. Save as:
   `bluestock_mf.pbix`
