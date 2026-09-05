import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Bluestock Mutual Fund Dashboard",
    page_icon="📊",
    layout="wide"
)
# ============================================================
# DATABASE PATH
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "bluestock_mf.db"
# ============================================================
# DATABASE CONNECTION
# ============================================================
@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
conn = get_connection()
# ============================================================
# TITLE
# ============================================================
st.title("📊 Bluestock Mutual Fund Analytics Dashboard")
st.markdown(
    """
    **Mutual Fund Business Intelligence & Analytics**

    This dashboard provides insights into fund performance, AUM,
    investor transactions, SIP trends, category inflows and
    portfolio sector exposure.
    """
)
st.divider()
# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    fund_master = pd.read_sql(
        "SELECT * FROM fund_master",
        conn
    )
    scheme_performance = pd.read_sql(
        "SELECT * FROM scheme_performance",
        conn
    )
    aum = pd.read_sql(
        "SELECT * FROM aum_by_fund_house",
        conn
    )
    category_inflows = pd.read_sql(
        "SELECT * FROM category_inflows",
        conn
    )
    sip = pd.read_sql(
        "SELECT * FROM monthly_sip_inflows",
        conn
    )
    transactions = pd.read_sql(
        "SELECT * FROM investor_transactions",
        conn
    )
    portfolio = pd.read_sql(
        "SELECT * FROM portfolio_holdings",
        conn
    )
    return (
        fund_master,
        scheme_performance,
        aum,
        category_inflows,
        sip,
        transactions,
        portfolio
    )
(
    fund_master,
    scheme_performance,
    aum,
    category_inflows,
    sip,
    transactions,
    portfolio
) = load_data()
# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.header("🔎 Dashboard Filters")
categories = sorted(
    scheme_performance["category"].dropna().unique()
)
selected_category = st.sidebar.selectbox(
    "Select Fund Category",
    ["All Categories"] + categories
)
# ============================================================
# FILTER PERFORMANCE DATA
# ============================================================
if selected_category == "All Categories":

    filtered_performance = scheme_performance.copy()

else:
    filtered_performance = scheme_performance[
        scheme_performance["category"] == selected_category
    ]
# ============================================================
# KPI SECTION
# ============================================================
st.subheader("📌 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        "Total Funds",
        len(fund_master)
    )
with col2:
    avg_return = filtered_performance[
        "return_3yr_pct"
    ].mean()
    st.metric(
        "Average 3-Year Return",
        f"{avg_return:.2f}%"
    )
with col3:
    latest_date = aum["date"].max()
    total_aum = aum[
        aum["date"] == latest_date
    ]["aum_crore"].sum()
    st.metric(
        "Total AUM",
        f"₹{total_aum:,.0f} Cr"
    )
with col4:
    total_transactions = len(transactions)
    st.metric(
        "Total Transactions",
        f"{total_transactions:,}"
    )
st.divider()
# ============================================================
# FUND PERFORMANCE
# ============================================================
st.subheader("🏆 Top Performing Funds")
top_funds = (
    filtered_performance
    .sort_values(
        "return_3yr_pct",
        ascending=False
    )
    .head(10)
)
col1, col2 = st.columns(2)
with col1:
    st.write("### Top 10 Funds by 3-Year Return")
    chart_data = top_funds[
        ["scheme_name", "return_3yr_pct"]
    ].set_index("scheme_name")
    st.bar_chart(
        chart_data
    )
with col2:
    st.write("### Fund Performance Table")
    display_data = top_funds[
        [
            "scheme_name",
            "category",
            "return_3yr_pct"
        ]
    ].copy()
    display_data.columns = [
        "Fund Name",
        "Category",
        "3-Year Return (%)"
    ]
    st.dataframe(
        display_data,
        width="stretch",
        hide_index=True
    )
st.divider()
# ============================================================
# FUND HOUSE AUM
# ============================================================
st.subheader("🏦 Fund House AUM")
aum_summary = (
    aum.groupby("fund_house")["aum_crore"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(
    aum_summary
)
st.divider()
# ============================================================
# CATEGORY INFLOWS
# ============================================================
st.subheader("💰 Category-wise Net Inflow")
category_summary = (
    category_inflows
    .groupby("category")["net_inflow_crore"]
    .sum()
    .sort_values(ascending=False)
)
st.bar_chart(
    category_summary
)
st.divider()
# ============================================================
# SIP TREND
# ============================================================
st.subheader("📈 SIP Inflow Trend")
sip["month"] = pd.to_datetime(
    sip["month"],
    errors="coerce"
)
sip = sip.sort_values("month")
sip_chart = sip.set_index("month")[
    [
        "sip_inflow_crore",
        "sip_aum_lakh_crore"
    ]
]
st.line_chart(
    sip_chart
)
st.divider()
# ============================================================
# TRANSACTION ANALYSIS
# ============================================================
st.subheader("💳 Investor Transaction Analysis")
transaction_summary = (
    transactions
    .groupby("transaction_type")["amount_inr"]
    .agg(
        transaction_count="count",
        total_amount="sum",
        average_amount="mean"
    )
    .sort_values(
        "total_amount",
        ascending=False
    )
)
col1, col2 = st.columns(2)
with col1:
    st.write("### Transaction Count")
    st.bar_chart(
        transaction_summary["transaction_count"]
    )
with col2:
    st.write("### Total Transaction Amount")
    st.bar_chart(
        transaction_summary["total_amount"]
    )
st.dataframe(
    transaction_summary,
    width="stretch"
)
st.divider()
# ============================================================
# SECTOR EXPOSURE
# ============================================================
st.subheader("🏭 Portfolio Sector Exposure")
sector_summary = (
    portfolio
    .groupby("sector")["weight_pct"]
    .mean()
    .sort_values(ascending=False)
)
st.bar_chart(
    sector_summary
)
st.divider()
# ============================================================
# FUND SEARCH
# ============================================================
st.subheader("🔍 Fund Search")
search_text = st.text_input(
    "Search fund name"
)
if search_text:
    search_result = fund_master[
        fund_master.astype(str)
        .apply(
            lambda row:
            row.str.contains(
                search_text,
                case=False,
                na=False
            ).any(),
            axis=1
        )
    ]
    st.dataframe(
        search_result,
        width="stretch",
        hide_index=True
    )
else:
    st.info(
        "Enter a fund name above to search."
    )
# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "Bluestock Mutual Fund Capstone Project | "
    "SQL + Python + Streamlit Analytics"
)