"""
Peer Comparison Streamlit Screen.
"""

import sys, os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import streamlit as st
from src.analytics.peer import PeerComparisonEngine
from src.reporting.charts import create_peer_radar_chart

st.set_page_config(page_title="Peer Comparison — Bluestock Nifty 100", layout="wide")

DB_PATH = "db/nifty100.db"
peer_engine = PeerComparisonEngine(DB_PATH)

st.title("⚔️ Peer Group Comparison & Percentile Benchmarking")

groups = peer_engine.get_peer_groups()
selected_group = st.selectbox("Select Peer Group:", groups)

st.markdown("---")

df_peers = peer_engine.get_peer_group_details(selected_group)
st.subheader(f"Peer Group: {selected_group}")

st.dataframe(df_peers, use_container_width=True)

if not df_peers.empty:
    st.markdown("### 🎯 Peer Group Radar Comparison")
    selected_comp = st.selectbox("Select Target Company for Radar:", df_peers["company_id"])
    target_row = df_peers[df_peers["company_id"] == selected_comp].iloc[0]

    comp_m = {
        "ROE Percentile": target_row["roe_percentile"],
        "FCF Percentile": target_row["fcf_percentile"],
        "NPM Percentile": target_row["npm_percentile"]
    }
    peer_avg = {
        "ROE Percentile": 50.0,
        "FCF Percentile": 50.0,
        "NPM Percentile": 50.0
    }

    fig = create_peer_radar_chart(selected_comp, comp_m, peer_avg)
    st.plotly_chart(fig, use_container_width=True)
