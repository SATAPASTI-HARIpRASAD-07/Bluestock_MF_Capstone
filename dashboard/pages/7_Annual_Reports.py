"""
Annual Reports & Document Repository Streamlit Screen.
"""

import sys, os
sys.path.insert(0, os.path.abspath('.'))

import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Annual Reports — Bluestock Nifty 100", layout="wide")

DB_PATH = "db/nifty100.db"

st.title("📂 Official Annual Reports & Document Repository")

conn = sqlite3.connect(DB_PATH)
df_docs = pd.read_sql_query("""
SELECT d.company_id, c.company_name, c.broad_sector, d.document_type, d.year, d.document_title, d.file_url
FROM documents d
JOIN companies c ON d.company_id = c.company_id
ORDER BY d.company_id ASC, d.year DESC
""", conn)
conn.close()

st.sidebar.header("Document Filter")
selected_comp = st.sidebar.selectbox("Filter by Company:", ["All"] + sorted(df_docs["company_id"].unique().tolist()))

if selected_comp != "All":
    df_docs = df_docs[df_docs["company_id"] == selected_comp]

st.subheader(f"Document Archive ({len(df_docs)} items)")
st.dataframe(df_docs, use_container_width=True)
