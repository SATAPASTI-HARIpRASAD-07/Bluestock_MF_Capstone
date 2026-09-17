"""
Trend & Growth Analytics Streamlit Screen.
"""

import sys, os
sys.path.insert(0, os.path.abspath('.'))

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from src.analytics.trends import TrendAnalyticsEngine

st.set_page_config(page_title="Trend Analysis — Bluestock Nifty 100", layout="wide")

DB_PATH = "db/nifty100.db"
trend_engine = TrendAnalyticsEngine(DB_PATH)

conn = sqlite3.connect(DB_PATH)
comp_list = pd.read_sql_query("SELECT company_id FROM companies ORDER BY company_id", conn)["company_id"].tolist()
conn.close()

st.title("📈 Historical Trend & CAGR Growth Analytics")

selected_comp = st.selectbox("Select Company for Trend Analysis:", comp_list)

st.markdown("---")

cagrs = trend_engine.compute_company_cagrs(selected_comp)
st.subheader(f"CAGR Summary — {selected_comp}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    s_3y = cagrs.get("sales_cr_cagr_3y", {}).get("cagr")
    st.metric("Revenue 3Y CAGR", f"{s_3y}%" if s_3y is not None else "N/A")
with col2:
    p_3y = cagrs.get("net_profit_cr_cagr_3y", {}).get("cagr")
    st.metric("PAT 3Y CAGR", f"{p_3y}%" if p_3y is not None else "N/A")
with col3:
    f_3y = cagrs.get("fcf_cagr_3y", {}).get("cagr")
    st.metric("FCF 3Y CAGR", f"{f_3y}%" if f_3y is not None else "N/A")
with col4:
    e_3y = cagrs.get("eps_cagr_3y", {}).get("cagr")
    st.metric("EPS 3Y CAGR", f"{e_3y}%" if e_3y is not None else "N/A")

st.markdown("---")

conn = sqlite3.connect(DB_PATH)
df_hist = pd.read_sql_query("""
SELECT r.year, p.sales_cr, p.net_profit_cr, r.cash_from_operations_cr as cfo, r.free_cash_flow_cr as fcf
FROM financial_ratios r
LEFT JOIN profitandloss p ON r.company_id = p.company_id AND r.year = p.year
WHERE r.company_id = ? ORDER BY r.year ASC
""", conn, params=(selected_comp,))
conn.close()

if not df_hist.empty:
    fig_rev = px.line(df_hist, x="year", y=["sales_cr", "net_profit_cr", "cfo", "fcf"],
                      title=f"Historical Financial Growth Trajectory (Rs Cr) — {selected_comp}", markers=True)
    st.plotly_chart(fig_rev, use_container_width=True)
