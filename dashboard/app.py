"""
Bluestock Nifty 100 Financial Intelligence Platform — Streamlit Dashboard.
"""

import sys
import os

sys.path.insert(0, os.path.abspath('.'))

import sqlite3
import pandas as pd
import streamlit as st
from db.loader import DatabaseBuilder
from src.analytics.health_score import FinancialHealthScoreEngine
from src.analytics.sector import SectorAnalyticsEngine

# Ensure Database exists on Cloud Deployment
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "nifty100.db")
if not os.path.exists(DB_PATH):
    builder = DatabaseBuilder(db_path=DB_PATH)
    builder.build_database()

st.set_page_config(
    page_title="Bluestock Nifty 100 Financial Intelligence Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 13px;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Bluestock Fintech — Nifty 100 Financial Intelligence Platform")
st.subheader("Production-Grade Financial Statement Analysis, Screener & Portfolio Intelligence")

st.markdown("---")

@st.cache_data
def load_overview_stats():
    conn = sqlite3.connect(DB_PATH)
    query = """
    WITH LatestYears AS (
        SELECT company_id, MAX(year) as max_year
        FROM financial_ratios
        GROUP BY company_id
    )
    SELECT c.company_id, c.broad_sector, r.return_on_equity_pct as roe,
           r.debt_to_equity as de, m.pe_ratio as pe, m.market_cap_crore as mcap
    FROM companies c
    JOIN LatestYears ly ON c.company_id = ly.company_id
    JOIN financial_ratios r ON r.company_id = ly.company_id AND r.year = ly.max_year
    LEFT JOIN market_cap m ON m.company_id = ly.company_id AND m.year = ly.max_year
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df_overview = load_overview_stats()

# KPI Summary Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown('<div class="metric-card"><div class="metric-value">92</div><div class="metric-label">Nifty 100 Companies</div></div>', unsafe_allow_html=True)
with col2:
    avg_roe = df_overview["roe"].mean()
    st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_roe:.1f}%</div><div class="metric-label">Average ROE</div></div>', unsafe_allow_html=True)
with col3:
    med_pe = df_overview["pe"].median()
    st.markdown(f'<div class="metric-card"><div class="metric-value">{med_pe:.1f}x</div><div class="metric-label">Median P/E Ratio</div></div>', unsafe_allow_html=True)
with col4:
    tot_mcap = df_overview["mcap"].sum() / 100000.0
    st.markdown(f'<div class="metric-card"><div class="metric-value">Rs. {tot_mcap:.1f}L Cr</div><div class="metric-label">Total Market Cap</div></div>', unsafe_allow_html=True)
with col5:
    debt_free = (df_overview["de"] == 0).sum()
    st.markdown(f'<div class="metric-card"><div class="metric-value">{debt_free}</div><div class="metric-label">Debt-Free Entities</div></div>', unsafe_allow_html=True)

st.markdown("---")

col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown("### 📊 Sector Breakdown & Market Weight")
    sec_engine = SectorAnalyticsEngine(DB_PATH)
    sec_df = sec_engine.get_sector_summary()
    st.dataframe(sec_df, hide_index=True, use_container_width=True)

with col_b:
    st.markdown("### 🛡️ Financial Health Score Overview")
    st.write("Distribution of Nifty 100 companies across Bluestock Financial Health Bands (0 to 100 Score):")
    st.info("• Excellent (80-100): High Quality & Low Solvency Risk\n• Good (60-79): Moderate Compounders\n• Fair (40-59): Average Operational Health\n• Weak/Critical (<40): High Risk Entities")

st.markdown("---")
st.caption("Bluestock Fintech Internship Capstone Project | Historical Intelligence Platform")