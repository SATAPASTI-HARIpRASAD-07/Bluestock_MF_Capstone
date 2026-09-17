"""
Sector Analytics Streamlit Screen.
"""

import sys, os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import streamlit as st
import plotly.express as px
from src.analytics.sector import SectorAnalyticsEngine

st.set_page_config(page_title="Sector Analytics — Bluestock Nifty 100", layout="wide")

DB_PATH = "db/nifty100.db"
sector_engine = SectorAnalyticsEngine(DB_PATH)

st.title("🏭 Sector Intelligence & Relative Benchmarks")

sec_summary = sector_engine.get_sector_summary()

st.subheader("Sector Level Financial Medians")
st.dataframe(sec_summary, use_container_width=True)

st.markdown("---")

st.subheader("Sector Valuation vs Profitability Bubble Map")
fig_bubble = px.scatter(sec_summary, x="median_pe", y="median_roe", size="total_mcap", color="broad_sector",
                        hover_name="broad_sector", text="broad_sector",
                        title="Median P/E vs Median ROE by Sector (Bubble Size = Market Cap)",
                        labels={"median_pe": "Median P/E Ratio", "median_roe": "Median ROE (%)"})
st.plotly_chart(fig_bubble, use_container_width=True)
