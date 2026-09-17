"""
Company Profile Deep-Dive Screen.
"""

import sys, os
sys.path.insert(0, os.path.abspath('.'))

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from src.analytics.ratios import FinancialRatioEngine
from src.analytics.health_score import FinancialHealthScoreEngine
from src.intelligence.pros_cons import ProsAndConsGenerator
from src.analytics.valuation import ValuationEngine

st.set_page_config(page_title="Company Profile — Bluestock Nifty 100", layout="wide")

DB_PATH = "db/nifty100.db"
ratio_engine = FinancialRatioEngine(DB_PATH)
health_engine = FinancialHealthScoreEngine(DB_PATH)
pros_cons_engine = ProsAndConsGenerator(DB_PATH)
val_engine = ValuationEngine(DB_PATH)

conn = sqlite3.connect(DB_PATH)
comp_list = pd.read_sql_query("SELECT company_id, company_name FROM companies ORDER BY company_id", conn)
conn.close()

st.title("🏢 Company Financial Profile & Deep-Dive Analytics")

selected_ticker = st.selectbox("Select Company:", comp_list["company_id"] + " — " + comp_list["company_name"])
ticker = selected_ticker.split(" — ")[0]

st.markdown("---")

# Fetch data
df_ratios = ratio_engine.get_company_ratios(ticker)
health = health_engine.compute_score_for_company(ticker)
obs = pros_cons_engine.generate_observations(ticker)
val_flag = val_engine.get_valuation_flag(ticker)

# Top Bar
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.subheader(f"📌 {ticker} Summary")
    st.metric("Financial Health Score", f"{health['score']} / 100", delta=health['band'])

with col2:
    st.subheader("💡 Valuation Status")
    st.info(f"**{val_flag['flag']}**: {val_flag['description']}")

with col3:
    if st.button("📄 Generate PDF Tear Sheet"):
        from src.reporting.pdf_reports import PDFReportGenerator
        pdf_gen = PDFReportGenerator(DB_PATH)
        pdf_path = pdf_gen.generate_company_tearsheet(ticker)
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name=f"{ticker}_tearsheet.pdf", mime="application/pdf")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Financial Statements & Trends", "🛡️ Health Score Breakdown", "💡 Pros & Cons", "📂 Annual Reports"])

with tab1:
    st.subheader("Historical Ratio & Margin Trends")
    if not df_ratios.empty:
        fig_margins = px.line(df_ratios, x="year", y=["net_profit_margin_pct", "operating_profit_margin_pct", "return_on_equity_pct"],
                             title=f"{ticker} Margin & Return Trends (%)", markers=True)
        st.plotly_chart(fig_margins, use_container_width=True)

        st.subheader("Financial Ratios Data Table")
        st.dataframe(df_ratios, use_container_width=True)

with tab2:
    st.subheader("Score Components Breakdown")
    for category, score in health["breakdown"].items():
        st.write(f"**{category}**: {score:.1f} pts")

with tab3:
    st.subheader("Observed Positive Drivers (Pros)")
    for p in obs["pros"]:
        st.success(f"• {p['text']} *(Trigger: {p['rule_triggered']})*")
    st.subheader("Observed Risk Factors (Cons)")
    for c in obs["cons"]:
        st.error(f"• {c['text']} *(Trigger: {c['rule_triggered']})*")

with tab4:
    st.subheader("Official Document Repository")
    conn = sqlite3.connect(DB_PATH)
    docs = pd.read_sql_query("SELECT document_title, year, file_url FROM documents WHERE company_id = ?", conn, params=(ticker,))
    conn.close()
    st.dataframe(docs, use_container_width=True)
