# Bluestock Fintech — Nifty 100 Financial Intelligence Platform

Production-quality financial intelligence platform analyzing the Nifty 100 universe of 92 companies for Bluestock Fintech.

---

## 🚀 Quick Start

### 1. Installation
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Run Full Master Pipeline (ETL -> Database -> KPIs -> Reports -> Tests)
```bash
python scripts/build_all.py
```

### 3. Launch Interactive Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```

### 4. Launch FastAPI REST Service Layer
```bash
uvicorn api.main:app --port 8000
```
Open interactive Swagger API docs at `http://localhost:8000/docs`.

---

## 📊 Core Features & Architecture

- **92 Nifty 100 Companies**: Analyzed across 11 broad sectors and peer groups.
- **50+ Financial KPIs**: Profitability (ROE, ROCE, OPM, NPM), Solvency (D/E, Interest Coverage), Cash Flow (CFO/PAT quality, FCF conversion/yield), Valuation (P/E, P/B, EV/EBITDA), Growth (1Y, 3Y, 5Y, 10Y CAGRs).
- **0–100 Financial Health Score**: Explainable, transparent scoring engine with risk bands.
- **Investment Screener**: Preset screens (Quality, Value, Growth, Dividend, Momentum, Debt-Free) & custom multi-metric filters.
- **Cash Flow Intelligence**: CFO/PAT earnings quality classification, CapEx intensity, 8-pattern capital allocation treemap.
- **Peer Comparison**: Within-peer group percentile rankings (0–100) and Plotly radar benchmark charts.
- **Automated Reporting**: 2-page ReportLab PDF Tear Sheets in `reports/company/` & openpyxl Excel exports in `outputs/`.
- **FastAPI Service**: 16 OpenAPI endpoints for seamless integration.

---

## 📂 Project Structure

```text
Bluestock_MF_Capstone/
│
├── config/
│   └── screener_config.yaml
│
├── data/
│   └── raw/
│
├── db/
│   ├── schema.sql
│   ├── loader.py
│   └── nifty100.db
│
├── src/
│   ├── etl/
│   ├── analytics/
│   ├── intelligence/
│   ├── reporting/
│   └── utils/
│
├── api/
│   └── main.py
│
├── dashboard/
│   ├── app.py
│   └── pages/
│
├── tests/
│   ├── etl/
│   ├── kpi/
│   ├── dq/
│   ├── api/
│   └── regression/
│
├── reports/
│   └── company/
│
├── outputs/
│
├── docs/
│   ├── data_quality_findings.md
│   ├── architecture.md
│   ├── methodology.md
│   ├── final_acceptance_report.md
│   └── internship_project_summary.md
│
├── scripts/
│   ├── test_db.py
│   └── build_all.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧪 Testing & Validation

Run the pytest suite:
```bash
pytest tests/ -v
```

All 20 unit, integration, and pipeline regression tests pass with zero errors.

---
*Bluestock Fintech Data Analytics Internship Project*