# BLUESTOCK FINTECH — MUTUAL FUND ANALYTICS PLATFORM

Complete 7-Day End-to-End Mutual Fund Analytics Capstone Project built using **Python, Pandas, SQLite, SQLAlchemy, Matplotlib, Seaborn, Streamlit, ReportLab, and Python-PPTX**.

---

## 🎯 Executive Summary & Objectives

The **Bluestock Mutual Fund Analytics Platform** provides a comprehensive data engineering, risk modeling, performance analytics, and business intelligence solution for retail and institutional mutual fund analytics.

### Key Objectives:
1. **Automated ETL Pipeline**: Ingestion, validation, deduplication, and cleaning across 10 raw datasets.
2. **Relational / Star Schema Data Modeling**: Population of SQLite database (`db/bluestock_mf.db`) containing dimensional and fact tables with primary/foreign keys and index optimizations.
3. **Risk & Return Analytics**: Calculation of 1Yr Return, 3Yr CAGR, 5Yr CAGR, Sharpe Ratio, Sortino Ratio, Annualized Volatility, Max Drawdown, Alpha, and Beta.
4. **Composite Fund Scorecard**: 0–100 weighted fund ranking system (30% 3Yr Return, 25% Sharpe, 20% Alpha, 15% Expense Ratio inverse, 10% Max Drawdown inverse).
5. **Advanced Quantitative Analytics**: Historical 95% VaR, CVaR, 90-Day Rolling Sharpe, Investor Cohort Analysis, SIP Continuity (at-risk gap detection), and Sector Concentration Herfindahl-Hirschman Index (HHI).
6. **Transparent Fund Recommender Engine**: Rule-based recommendation model providing risk-profile-matched top fund selections with non-financial advice disclaimers.
7. **Interactive Streamlit Dashboard**: 4-page interactive BI dashboard with multi-level slicers for fund houses, categories, plans, states, age groups, and city tiers.
8. **Automated Final Report & Presentation**: PDF project report (24 sections) and 12-slide PowerPoint presentation deck (`reports/`).

---

## 🏗️ System Architecture

```text
                                  +-----------------------+
                                  |   Raw CSV Datasets    |
                                  |      (data/raw/)      |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |   Live NAV API /      |
                                  |   Local ETL Pipeline  |
                                  | (scripts/etl_pipeline)|
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |  Cleaned Processed    |
                                  |      CSV Files        |
                                  |   (data/processed/)   |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |  SQLite Star Schema   |
                                  |  (db/bluestock_mf.db) |
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                        |                        |
                     v                        v                        v
          +--------------------+    +--------------------+    +--------------------+
          |  Risk & Return     |    | Advanced Analytics |    | Streamlit BI       |
          |  Metrics & Ratios  |    |  VaR, CVaR, HHI,   |    | Web Dashboard      |
          | (compute_metrics)  |    | Cohorts, Continuity|    | (dashboard/app.py) |
          +---------+----------+    +---------+----------+    +--------------------+
                    |                         |
                    +-------------------------+
                                              |
                                              v
                                  +-----------------------+
                                  | Generated PDF Report  |
                                  | & PowerPoint Deck     |
                                  | (reports/ & charts/)  |
                                  +-----------------------+
```

---

## 📁 Project Folder Structure

```text
bluestock_mf_capstone/
├── data/
│   ├── raw/                       # 10 Original CSV Datasets
│   └── processed/                 # Cleaned & Validated Processed Datasets
├── db/
│   └── bluestock_mf.db            # SQLite Star Schema Database
├── notebooks/                     # Jupyter Notebooks (Day 1 - Day 6)
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_performance_analytics.ipynb
│   └── 05_advanced_analytics.ipynb
├── scripts/                       # Core Analytics & Pipeline Scripts
│   ├── live_nav_fetch.py          # Live NAV API Ingestion & Offline Fallback
│   ├── etl_pipeline.py            # Master Data Cleaning & Database ETL
│   ├── compute_metrics.py         # Performance, Risk Ratios & Fund Scorecard
│   ├── advanced_analytics.py      # VaR, CVaR, Cohorts, Continuity & HHI Index
│   ├── recommender.py             # Rule-Based Fund Recommendation Engine
│   ├── generate_charts.py         # 16 High-Resolution Visualization Charts
│   ├── generate_report.py         # Automated 24-Section PDF Final Report
│   └── generate_presentation.py   # Automated 12-Slide PowerPoint Deck
├── sql/                           # SQL DDL & Analytical Queries
│   ├── schema.sql                 # DDL Schema Script
│   └── queries.sql                # 12 Analytical SQL Queries
├── dashboard/
│   └── app.py                     # 4-Page Streamlit BI Dashboard Application
├── reports/                       # Generated Final Submissions
│   ├── Final_Report.pdf           # Comprehensive Final PDF Report
│   └── Bluestock_MF_Presentation.pptx # 12-Slide Presentation Deck
├── charts/                        # 16 PNG Visualizations
├── outputs/                       # Analytical Output CSV Datasets
│   ├── fund_scorecard.csv
│   ├── alpha_beta.csv
│   ├── var_cvar_report.csv
│   ├── cohort_analysis.csv
│   ├── sip_continuity.csv
│   └── sector_hhi.csv
├── logs/                          # Execution Logs
├── tests/                         # Automated Pytest Suite
│   └── test_pipeline.py
├── requirements.txt               # Dependencies List
├── run_pipeline.py                # Master End-to-End Execution Script
├── README.md                      # Project Documentation
└── data_dictionary.md             # Dataset & Schema Dictionary
```

---

## ⚡ Quick Start & Pipeline Execution

### 1. Environment Setup

Ensure Python 3.10+ is installed. Clone or navigate to the project directory:

```bash
python -m venv .venv
.venv\Scripts\activate        # On Windows
pip install -r requirements.txt
```

### 2. Execute Master End-to-End Pipeline

Run the master pipeline script to execute all ingestion, cleaning, database creation, metric computations, advanced analytics, chart generation, report compilation, and validation in sequence:

```bash
python run_pipeline.py
```

### 3. Launch Interactive Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

### 4. Run Automated Test Suite

```bash
pytest tests/
```

---

## 📊 Summary of Master Outputs

| Deliverable | File Location | Description |
|---|---|---|
| **SQLite Database** | `db/bluestock_mf.db` | Normalized Star Schema DB with dimensions and 8 fact tables |
| **Fund Scorecard** | `outputs/fund_scorecard.csv` | Composite 0-100 fund ranking across 40 schemes |
| **Benchmark Report** | `outputs/alpha_beta.csv` | Alpha, Beta, Sharpe & excess return benchmark analysis |
| **VaR & CVaR Report** | `outputs/var_cvar_report.csv` | Historical 95% VaR and Conditional VaR tail loss metrics |
| **Investor Cohorts** | `outputs/cohort_analysis.csv` | Retention, total investment & SIP activity by cohort year |
| **SIP Continuity** | `outputs/sip_continuity.csv` | Investor transaction gaps and at-risk flag analysis |
| **Sector HHI Index** | `outputs/sector_hhi.csv` | Herfindahl-Hirschman Concentration Index per fund scheme |
| **Visualizations** | `charts/` | 16 High-resolution PNG charts covering EDA and risk |
| **Final PDF Report** | `reports/Final_Report.pdf` | Comprehensive 24-section publication-ready report |
| **Presentation Deck** | `reports/Bluestock_MF_Presentation.pptx` | 12-slide PowerPoint presentation deck |

---

## 🔒 Data Authenticity & Educational Disclaimer

- **Data Authenticity Notice**: Mutual fund metadata, NAV histories, AUM figures, category inflows, portfolio holdings, and benchmark index values reflect anchored real public market data. Investor transaction records were synthetically generated to model realistic retail investor behavior while maintaining privacy compliance.
- **Educational Disclaimer**: The analytics, risk metrics, and recommendation models contained in this repository are developed strictly for academic and project evaluation purposes. They **DO NOT** constitute professional financial, investment, or legal advice.