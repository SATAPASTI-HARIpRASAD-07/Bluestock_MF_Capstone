# Bluestock Mutual Fund Capstone Project
## 📊 Mutual Fund Data Analytics & Interactive Dashboard
A complete data analytics project built using **Python, SQL, Pandas, Matplotlib, SQLite, and Streamlit** to analyze mutual fund performance, assets under management, SIP trends, investor transactions, portfolio exposure, and benchmark indices
---
## 🎯 Project Objective
The objective of this project is to transform raw mutual fund datasets into meaningful business insights through:
- Data inspection
- Data cleaning
- Data preprocessing
- SQL database creation
- SQL-based analysis
- Business insights generation
- Data visualization
- Interactive Streamlit dashboard
The project provides an analytical view of mutual fund performance and investor-related trends.
---
## 🛠️ Technologies Used
| Technology | Purpose |
|---|---|
| Python | Data processing and analysis |
| Pandas | Data cleaning and manipulation |
| SQLite | Database storage |
| SQLAlchemy | Loading data into SQL |
| SQL | Data analysis and aggregation |
| Matplotlib | Data visualization |
| Streamlit | Interactive dashboard |
| VS Code | Development environment |
| Git | Version control |
---
## 📁 Project Structure
```text
Bluestock_MF_Capstone/
│
├── .venv/
│
├── data/
│   ├── raw/
│   │   └── Original CSV datasets
│   │
│   └── processed/
│       ├── 01_fund_master.csv
│       ├── 02_nav_history.csv
│       ├── 03_aum_by_fund_house.csv
│       ├── 04_monthly_sip_inflows.csv
│       ├── 05_category_inflows.csv
│       ├── 06_industry_folio_count.csv
│       ├── 07_scheme_performance.csv
│       ├── 08_investor_transactions.csv
│       ├── 09_portfolio_holdings.csv
│       └── 10_benchmark_indices.csv
│
├── analysis/
│   └── business_insights.py
│
├── dashboard/
│   └── app.py
│
├── visualizations/
│   ├── create_charts.py
│   ├── category_performance.png
│   ├── top_10_funds.png
│   ├── fund_house_aum.png
│   ├── category_net_inflow.png
│   ├── sip_inflow_trend.png
│   ├── transaction_types.png
│   ├── state_transactions.png
│   └── sector_exposure.png
│
├── clean_data.py
├── inspect_data.py
├── inspection_report.txt
├── load_to_sql.py
├── sql_analysis.py
├── bluestock_mf.db
└── README.md
```
---
# 📦 Datasets
The project contains 10 mutual fund datasets.
### 1. Fund Master
Contains information about mutual fund schemes including:
- AMFI code
- Fund house
- Scheme name
- Category
- Sub-category
- Plan
- Launch date
- Benchmark
---
### 2. NAV History

Contains historical Net Asset Value information for mutual fund schemes.

Used for analyzing historical fund performance.

---

### 3. AUM by Fund House

Contains Assets Under Management information for different mutual fund houses.

Used to analyze:

- Fund house AUM
- Average AUM
- Maximum AUM
- Fund house comparison

---

### 4. Monthly SIP Inflows

Contains monthly SIP-related information.

Used for analyzing:

- SIP inflows
- Active SIP accounts
- New SIP accounts
- SIP AUM
- Year-over-year growth

The first 12 months contain missing YoY growth values because previous-year comparison data is not available for those months.

---

### 5. Category Inflows

Contains mutual fund category-wise inflow information.

Used to identify categories receiving higher net inflows.

---

### 6. Industry Folio Count

Contains industry-wise folio information.

Used to analyze investor participation across industries.

---

### 7. Scheme Performance

Contains performance-related metrics for mutual fund schemes.

Used to analyze:

- 3-year returns
- Sharpe ratio
- Fund categories
- Expense ratios
- Performance anomalies

---

### 8. Investor Transactions

Contains investor transaction information.

Used to analyze:

- SIP transactions
- Lumpsum transactions
- Redemptions
- Transaction amounts
- State-wise activity

---

### 9. Portfolio Holdings

Contains portfolio-level holding information.

Used to analyze:

- Sector exposure
- Holding weights
- Market values

---

### 10. Benchmark Indices

Contains historical benchmark index values.

Used for benchmark-level analysis and comparison.

---

# 🧹 Data Cleaning

The `clean_data.py` script performs the main preprocessing operations.

### Data cleaning workflow

```text
Raw CSV Files
      ↓
File Identification
      ↓
CSV Loading
      ↓
Data Cleaning
      ↓
Data Type Processing
      ↓
Validation
      ↓
Processed CSV Files
```

The processed datasets are stored inside:

```text
data/processed/
```

---

# 🔍 Data Inspection

The `inspect_data.py` script checks the datasets for:

- Number of rows
- Number of columns
- Column names
- Data types
- Missing values
- Sample records

The inspection results are stored in:

```text
inspection_report.txt
```

---

# 🗄️ SQL Database

The processed datasets are loaded into a SQLite database:

```text
bluestock_mf.db
```

The database contains 10 tables:

```text
fund_master
nav_history
aum_by_fund_house
monthly_sip_inflows
category_inflows
industry_folio_count
scheme_performance
investor_transactions
portfolio_holdings
benchmark_indices
```

---

# 📈 SQL Analysis

The `sql_analysis.py` script performs analytical queries on the database.

Major analyses include:

### 1. Fund Performance by Category

Identifies average 3-year performance across mutual fund categories.

### 2. Top 10 Funds by 3-Year Return

Identifies schemes with the highest 3-year returns.

### 3. Top Funds by Sharpe Ratio

Analyzes risk-adjusted performance.

### 4. Fund House AUM

Compares AUM across mutual fund houses.

### 5. SIP Inflow Trend

Analyzes monthly SIP trends.

### 6. Category-wise Net Inflow

Identifies categories receiving higher net inflows.

### 7. Transaction Type Analysis

Compares:

- SIP
- Lumpsum
- Redemption

### 8. State-wise Investor Transactions

Analyzes transaction activity across states.

### 9. Portfolio Sector Exposure

Analyzes average portfolio exposure across sectors.

### 10. Benchmark Index Summary

Analyzes historical benchmark index values.

---

# 💡 Business Insights

The `analysis/business_insights.py` script generates important business-level insights.

## Best Performing Categories

Based on the analyzed 3-year return data:

| Category | Average 3-Year Return (%) |
|---|---:|
| Small Cap | 21.69 |
| Mid Cap | 16.59 |
| Flexi Cap | 15.50 |
| Value | 14.76 |
| Large & Mid Cap | 14.56 |
| ELSS | 13.58 |
| Large Cap | 12.99 |
| Index | 12.10 |
| Index/ETF | 11.77 |
| Short Duration | 7.37 |
| Liquid | 6.33 |
| Gilt | 5.69 |

Small Cap had the highest average 3-year return among the analyzed categories.

---

## Top Performing Funds

The top funds by 3-year return included:

1. SBI Small Cap Regular
2. SBI Small Cap Direct
3. ABSL Small Cap Regular
4. Axis Small Cap Regular
5. Nippon India Small Cap Regular
6. DSP Small Cap Regular
7. Kotak Emerging Equity Mid Cap
8. ICICI Pru Midcap
9. DSP Midcap
10. HDFC Mid-Cap Opportunities

---

## SIP Analysis

The dataset contains monthly SIP information from 2022 through 2025.

The analysis can be used to understand:

- SIP inflow growth
- Active SIP account trends
- New SIP account additions
- SIP AUM growth

---

## Investor Transaction Analysis

The transaction dataset contains:

| Transaction Type | Number of Transactions | Average Amount (INR) |
|---|---:|---:|
| SIP | 19,716 | 11,018.13 |
| Lumpsum | 8,095 | 254,456.02 |
| Redemption | 4,967 | 250,558.79 |

SIP transactions have a much smaller average transaction amount compared with lumpsum and redemption transactions.

---

## Portfolio Sector Exposure

The portfolio analysis calculates average sector exposure rather than simply summing holding weights across all funds.

Major sectors analyzed include:

- Consumer Goods
- Diversified
- IT
- Utilities
- FMCG
- Banking
- NBFC
- Pharma
- Automobile
- Telecom
- Energy
- Paints
- Cement
- Infrastructure

---

# 📊 Data Visualizations

The project generates 8 major visualizations.

### 1. Category Performance

```text
visualizations/category_performance.png
```

Shows average 3-year performance by mutual fund category.

### 2. Top 10 Funds

```text
visualizations/top_10_funds.png
```

Shows the highest-performing funds based on 3-year return.

### 3. Fund House AUM

```text
visualizations/fund_house_aum.png
```

Compares AUM across fund houses.

### 4. Category Net Inflow

```text
visualizations/category_net_inflow.png
```

Shows category-wise net inflows.

### 5. SIP Inflow Trend

```text
visualizations/sip_inflow_trend.png
```

Shows monthly SIP trends.

### 6. Transaction Types

```text
visualizations/transaction_types.png
```

Compares SIP, lumpsum, and redemption transactions.

### 7. State Transactions

```text
visualizations/state_transactions.png
```

Shows transaction activity across states.

### 8. Sector Exposure

```text
visualizations/sector_exposure.png
```

Shows average portfolio exposure across sectors.

---

# 🖥️ Interactive Streamlit Dashboard

The project includes an interactive Streamlit dashboard.

Main application:

```text
dashboard/app.py
```

The dashboard provides:

- Fund search
- Fund category filtering
- Performance analysis
- Fund house AUM analysis
- SIP trends
- Investor transaction analysis
- Portfolio sector exposure
- Interactive data tables
- Business insights

---

# ▶️ How to Run the Project

## Step 1 — Activate Virtual Environment

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Git Bash

```bash
source .venv/Scripts/activate
```

---

## Step 2 — Install Dependencies

```bash
pip install pandas matplotlib sqlalchemy streamlit
```

---

## Step 3 — Clean the Data

```bash
python clean_data.py
```

---

## Step 4 — Inspect the Data

```bash
python inspect_data.py
```

---

## Step 5 — Load Data into SQLite

```bash
python load_to_sql.py
```

This creates:

```text
bluestock_mf.db
```

---

## Step 6 — Run SQL Analysis

```bash
python sql_analysis.py
```

---

## Step 7 — Generate Business Insights

```bash
python analysis/business_insights.py
```

---

## Step 8 — Generate Visualizations

```bash
python visualizations/create_charts.py
```

---

## Step 9 — Run Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

The Streamlit application will open in your web browser.

---

# 🔄 Complete Project Workflow

```text
              RAW DATA
                 │
                 ▼
        ┌─────────────────┐
        │ Data Inspection │
        └─────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Data Cleaning   │
        └─────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Processed CSVs  │
        └─────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ SQLite Database │
        └─────────────────┘
                 │
          ┌──────┴──────┐
          ▼             ▼
     SQL Analysis   Python Analysis
          │             │
          └──────┬──────┘
                 ▼
        ┌─────────────────┐
        │ Business        │
        │ Insights        │
        └─────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Visualizations  │
        └─────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Streamlit       │
        │ Dashboard       │
        └─────────────────┘
```

---

# 🎯 Key Project Outcomes

This project demonstrates practical skills in:

- Data cleaning
- Data preprocessing
- Exploratory data analysis
- SQL querying
- SQLite database management
- Business analytics
- Financial data analysis
- Data visualization
- Dashboard development
- Python programming

---

# 📌 Conclusion

The Bluestock Mutual Fund Capstone Project converts raw mutual fund datasets into a structured analytical solution.

The combination of **Python + SQL + Visualization + Streamlit** provides an end-to-end data analytics workflow that can help understand:

- Mutual fund performance
- Fund category trends
- Fund house AUM
- SIP growth
- Investor transactions
- Portfolio sector exposure
- Benchmark movements

The final Streamlit dashboard provides an interactive interface for exploring these insights.

---

## 👨‍💻 Project

**Bluestock Mutual Fund Capstone Project**

**Technology Stack:**

```text
Python
Pandas
SQL
SQLite
SQLAlchemy
Matplotlib
Streamlit
VS Code
```