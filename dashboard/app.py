import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Bluestock Mutual Fund Analytics Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "bluestock_mf.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "bluestock_mf.db"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

# ============================================================
# LOAD DATA WITH CACHING
# ============================================================
@st.cache_data
def load_all_data():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    
    fund_master = pd.read_sql("SELECT * FROM fund_master", conn)
    scheme_perf = pd.read_sql("SELECT * FROM scheme_performance", conn)
    aum = pd.read_sql("SELECT * FROM aum_by_fund_house", conn)
    cat_inflows = pd.read_sql("SELECT * FROM category_inflows", conn)
    sip = pd.read_sql("SELECT * FROM monthly_sip_inflows", conn)
    transactions = pd.read_sql("SELECT * FROM investor_transactions", conn)
    portfolio = pd.read_sql("SELECT * FROM portfolio_holdings", conn)
    benchmark = pd.read_sql("SELECT * FROM benchmark_indices", conn)
    nav = pd.read_sql("SELECT * FROM nav_history", conn)
    folio = pd.read_sql("SELECT * FROM industry_folio_count", conn)
    
    conn.close()
    return fund_master, scheme_perf, aum, cat_inflows, sip, transactions, portfolio, benchmark, nav, folio

fund_master, scheme_perf, aum, cat_inflows, sip, transactions, portfolio, benchmark, nav, folio = load_all_data()

# Load Scorecard if available
scorecard_path = OUTPUT_DIR / "fund_scorecard.csv"
if scorecard_path.exists():
    df_scorecard = pd.read_csv(scorecard_path)
else:
    df_scorecard = scheme_perf.copy()

# ============================================================
# HEADER & NAVIGATION
# ============================================================
st.title("📊 Bluestock Mutual Fund Analytics Platform")
st.caption("Interactive Business Intelligence, Risk Analytics & Fund Performance Dashboard")

tabs = st.tabs([
    "🏛️ Page 1: Industry Overview",
    "🏆 Page 2: Fund Performance & Scorecard",
    "👥 Page 3: Investor Analytics",
    "📈 Page 4: SIP & Market Trends"
])

# ============================================================
# PAGE 1: INDUSTRY OVERVIEW
# ============================================================
with tabs[0]:
    st.header("Industry Overview & Macro Trends")
    st.markdown("Macro-level metrics across AUM, industry SIP inflows, folio counts, and scheme distributions.")
    
    # Top KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        # Industry AUM: ₹81 Lakh Crore (₹8,100,000 Cr); Top 10 AMCs AUM: ₹62.74 Lakh Cr (₹6,274,000 Cr)
        st.metric("Total Industry AUM", "₹81.00 Lakh Cr", delta="Top 10 AMCs: ₹62.74 Lakh Cr", delta_color="normal")
    with col2:
        latest_sip = sip.sort_values("month").iloc[-1]
        st.metric("Monthly SIP Inflow", f"₹{latest_sip['sip_inflow_crore']:,.0f} Cr", delta=f"{latest_sip['yoy_growth_pct']}% YoY")
    with col3:
        latest_folio = folio.sort_values("month").iloc[-1]
        st.metric("Total Folio Count", f"{latest_folio['total_folios_crore']:.2f} Cr")
    with col4:
        st.metric("Industry Schemes", "1,908")
    with col5:
        st.metric("Schemes Analyzed", f"{len(fund_master)}")
        
    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Industry AUM Growth Trajectory")
        aum_trend = aum.groupby("date")["aum_crore"].sum().reset_index()
        aum_trend["date"] = pd.to_datetime(aum_trend["date"])
        aum_trend = aum_trend.sort_values("date")
        st.line_chart(aum_trend.set_index("date")["aum_crore"])
        
    with col_b:
        st.subheader("Top Fund Houses by Average AUM")
        top_fh = aum.groupby("fund_house")["aum_crore"].mean().sort_values(ascending=False).head(10)
        st.bar_chart(top_fh)

# ============================================================
# PAGE 2: FUND PERFORMANCE & SCORECARD
# ============================================================
with tabs[1]:
    st.header("Fund Performance, Risk Scatter & Scorecard")
    
    # Slicers
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        cat_filter = st.selectbox("Filter Category", ["All Categories"] + sorted(scheme_perf["category"].dropna().unique()))
    with col_s2:
        fh_filter = st.selectbox("Filter Fund House", ["All Fund Houses"] + sorted(scheme_perf["fund_house"].dropna().unique()))
    with col_s3:
        plan_filter = st.selectbox("Filter Plan", ["All Plans"] + sorted(scheme_perf["plan"].dropna().unique()))

    # Filter data
    filtered_perf = scheme_perf.copy()
    if cat_filter != "All Categories":
        filtered_perf = filtered_perf[filtered_perf["category"] == cat_filter]
    if fh_filter != "All Fund Houses":
        filtered_perf = filtered_perf[filtered_perf["fund_house"] == fh_filter]
    if plan_filter != "All Plans":
        filtered_perf = filtered_perf[filtered_perf["plan"] == plan_filter]

    st.subheader("Composite Fund Scorecard & Metrics")
    st.dataframe(
        filtered_perf[[
            "scheme_name", "category", "fund_house", "plan", 
            "return_3yr_pct", "sharpe_ratio", "alpha", "beta", "expense_ratio_pct", "max_drawdown_pct"
        ]].sort_values("return_3yr_pct", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("Risk (Volatility) vs Return (3Yr CAGR)")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(
            data=filtered_perf,
            x="std_dev_ann_pct",
            y="return_3yr_pct",
            hue="category",
            s=100,
            ax=ax
        )
        ax.set_title("Risk vs Return Scatter Plot")
        ax.set_xlabel("Annualized Volatility (%)")
        ax.set_ylabel("3-Year Return (%)")
        st.pyplot(fig)
        
    with col_p2:
        st.subheader("Fund Return vs Benchmark Return")
        bm_comp = filtered_perf[["scheme_name", "return_3yr_pct", "benchmark_3yr_pct"]].head(10).set_index("scheme_name")
        st.bar_chart(bm_comp)

# ============================================================
# PAGE 3: INVESTOR ANALYTICS
# ============================================================
with tabs[2]:
    st.header("Investor Demographics & Transaction Analytics")
    
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        state_f = st.selectbox("Select State", ["All States"] + sorted(transactions["state"].dropna().unique()))
    with col_i2:
        age_f = st.selectbox("Select Age Group", ["All Age Groups"] + sorted(transactions["age_group"].dropna().unique()))
    with col_i3:
        tier_f = st.selectbox("Select City Tier", ["All Tiers"] + sorted(transactions["city_tier"].dropna().unique()))

    filtered_tx = transactions.copy()
    if state_f != "All States":
        filtered_tx = filtered_tx[filtered_tx["state"] == state_f]
    if age_f != "All Age Groups":
        filtered_tx = filtered_tx[filtered_tx["age_group"] == age_f]
    if tier_f != "All Tiers":
        filtered_tx = filtered_tx[filtered_tx["city_tier"] == tier_f]

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Transaction Amount by State (Top 10)")
        state_vol = filtered_tx.groupby("state")["amount_inr"].sum().sort_values(ascending=False).head(10) / 1e7
        st.bar_chart(state_vol)
        
    with col_t2:
        st.subheader("Transaction Type Split (SIP vs Lumpsum vs Redemption)")
        type_split = filtered_tx.groupby("transaction_type")["amount_inr"].sum() / 1e7
        st.bar_chart(type_split)

    st.subheader("Investor Age Group Breakdown")
    age_analysis = filtered_tx.groupby("age_group")["amount_inr"].agg(["count", "sum", "mean"]).reset_index()
    age_analysis.columns = ["Age Group", "Transaction Count", "Total Volume (INR)", "Average Amount (INR)"]
    st.dataframe(age_analysis, use_container_width=True, hide_index=True)

# ============================================================
# PAGE 4: SIP & MARKET TRENDS
# ============================================================
with tabs[3]:
    st.header("SIP Growth, Benchmark Indices & Category Inflows")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Monthly Industry SIP Inflow Trend")
        sip_sorted = sip.sort_values("month")
        sip_sorted["month"] = pd.to_datetime(sip_sorted["month"])
        st.line_chart(sip_sorted.set_index("month")["sip_inflow_crore"])
        
    with col_m2:
        st.subheader("Benchmark Index Performance Trajectory")
        bm_pivot = benchmark.pivot(index="date", columns="index_name", values="close_value")
        bm_pivot.index = pd.to_datetime(bm_pivot.index)
        st.line_chart(bm_pivot)

    st.subheader("Category Net Inflow Breakdown")
    cat_sum = cat_inflows.groupby("category")["net_inflow_crore"].sum().sort_values(ascending=False)
    st.bar_chart(cat_sum)

st.divider()
st.caption("Bluestock Fintech Mutual Fund Analytics Capstone Project | Master End-to-End Analytics Platform")