"""
Financial Screener Streamlit Screen.
"""

import sys, os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import streamlit as st
from src.analytics.screener import InvestmentScreener
from src.reporting.excel_reports import ExcelReportGenerator

st.set_page_config(page_title="Financial Screener — Bluestock Nifty 100", layout="wide")

DB_PATH = "db/nifty100.db"
screener = InvestmentScreener(DB_PATH)
excel_gen = ExcelReportGenerator(DB_PATH)

st.title("🔍 Nifty 100 Investment Screener")

st.sidebar.header("Preset Screens")
preset_choice = st.sidebar.selectbox("Choose Preset Screen:", ["Custom Filters", "quality", "value", "growth", "dividend", "momentum", "debt_free"])

st.markdown("---")

if preset_choice != "Custom Filters":
    st.subheader(f"Preset Screen: {preset_choice.upper()}")
    df_res = screener.run_preset(preset_choice)
else:
    st.subheader("Custom Multi-Metric Filter")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        min_roe = st.slider("Minimum ROE (%)", 0.0, 50.0, 15.0)
    with col2:
        max_de = st.slider("Maximum Debt-to-Equity", 0.0, 3.0, 1.0)
    with col3:
        min_fcf = st.slider("Minimum FCF (Rs Cr)", -1000.0, 5000.0, 0.0)
    with col4:
        max_pe = st.slider("Maximum P/E Ratio", 5.0, 100.0, 30.0)

    df_res = screener.run_custom(min_roe=min_roe, max_de=max_de, min_fcf=min_fcf, max_pe=max_pe)

st.write(f"**Found {len(df_res)} matching companies**")
st.dataframe(df_res, use_container_width=True)

if not df_res.empty:
    excel_path = excel_gen.generate_screener_excel(df_res, "screener_results.xlsx")
    with open(excel_path, "rb") as f:
        st.download_button("📊 Export Results to Excel", f, file_name="screener_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
