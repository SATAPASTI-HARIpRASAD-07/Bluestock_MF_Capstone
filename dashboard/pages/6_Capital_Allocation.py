"""
Capital Allocation Treemap Screen.
"""

import sys, os
sys.path.insert(0, os.path.abspath('.'))

import sqlite3
import pandas as pd
import streamlit as st
from src.analytics.cashflow import CashFlowIntelligenceEngine
from src.reporting.charts import create_capital_allocation_treemap

st.set_page_config(page_title="Capital Allocation — Bluestock Nifty 100", layout="wide")

DB_PATH = "db/nifty100.db"
cf_engine = CashFlowIntelligenceEngine(DB_PATH)

st.title("🗺️ Capital Allocation & Cash Flow Sign Matrix Treemap")
st.write("Group all 92 Nifty 100 companies by CFO / CFI / CFF Sign Patterns and Capital Allocation Strategies.")

@st.cache_data
def load_treemap_data():
    conn = sqlite3.connect(DB_PATH)
    comp_df = pd.read_sql_query("SELECT company_id, broad_sector FROM companies", conn)
    conn.close()

    records = []
    for _, r in comp_df.iterrows():
        cid = r["company_id"]
        res = cf_engine.analyze_company_cashflow(cid)
        if res.get("status") != "NO_DATA":
            records.append({
                "company_id": cid,
                "broad_sector": r["broad_sector"],
                "pattern_description": res["pattern_description"],
                "cfo_pat_ratio": res["cfo_pat_ratio"],
                "market_cap_crore": 50000.0 # Standard size anchor
            })
    return pd.DataFrame(records)

df_tree = load_treemap_data()

fig_tree = create_capital_allocation_treemap(df_tree)
st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("---")
st.subheader("Capital Allocation Breakdown Data")
st.dataframe(df_tree, use_container_width=True)
