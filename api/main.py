"""
FastAPI Service Application — Nifty 100 Financial Intelligence REST API.
"""

import sqlite3
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional

from src.analytics.screener import InvestmentScreener
from src.analytics.health_score import FinancialHealthScoreEngine
from src.analytics.sector import SectorAnalyticsEngine
from src.analytics.peer import PeerComparisonEngine
from src.analytics.statistics import PortfolioStatisticsEngine
from src.reporting.pdf_reports import PDFReportGenerator

app = FastAPI(
    title="Bluestock Nifty 100 Financial Intelligence REST API",
    description="Production-grade Financial Intelligence API serving Nifty 100 datasets, financial KPIs, investment screeners, and PDF tear sheets.",
    version="1.0.0"
)

DB_PATH = "db/nifty100.db"
screener_engine = InvestmentScreener(DB_PATH)
health_engine = FinancialHealthScoreEngine(DB_PATH)
sector_engine = SectorAnalyticsEngine(DB_PATH)
peer_engine = PeerComparisonEngine(DB_PATH)
stats_engine = PortfolioStatisticsEngine(DB_PATH)
pdf_engine = PDFReportGenerator(DB_PATH)

def query_db(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "Bluestock Nifty 100 API", "database": "connected"}

@app.get("/api/v1/companies", tags=["Companies"])
def list_companies():
    return query_db("SELECT * FROM companies ORDER BY company_id")

@app.get("/api/v1/companies/{ticker}", tags=["Companies"])
def get_company(ticker: str):
    res = query_db("SELECT * FROM companies WHERE company_id = ?", (ticker.upper(),))
    if not res:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")
    return res[0]

@app.get("/api/v1/companies/{ticker}/pl", tags=["Financial Statements"])
def get_company_pl(ticker: str):
    return query_db("SELECT * FROM profitandloss WHERE company_id = ? ORDER BY year ASC", (ticker.upper(),))

@app.get("/api/v1/companies/{ticker}/bs", tags=["Financial Statements"])
def get_company_bs(ticker: str):
    return query_db("SELECT * FROM balancesheet WHERE company_id = ? ORDER BY year ASC", (ticker.upper(),))

@app.get("/api/v1/companies/{ticker}/cashflow", tags=["Financial Statements"])
def get_company_cashflow(ticker: str):
    return query_db("SELECT * FROM cashflow WHERE company_id = ? ORDER BY year ASC", (ticker.upper(),))

@app.get("/api/v1/companies/{ticker}/ratios", tags=["Financial Ratios"])
def get_company_ratios(ticker: str):
    return query_db("SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year ASC", (ticker.upper(),))

@app.get("/api/v1/companies/{ticker}/tearsheet", tags=["Reporting"])
def download_tearsheet(ticker: str):
    pdf_path = pdf_engine.generate_company_tearsheet(ticker.upper())
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF Tear Sheet generation failed")
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{ticker.upper()}_tearsheet.pdf")

@app.get("/api/v1/screener", tags=["Analytics"])
def run_screener(preset: Optional[str] = None, min_roe: Optional[float] = None, max_de: Optional[float] = None):
    if preset:
        df = screener_engine.run_preset(preset)
    else:
        df = screener_engine.run_custom(min_roe=min_roe, max_de=max_de)
    return df.to_dict(orient="records")

@app.get("/api/v1/sectors", tags=["Sector Analytics"])
def list_sectors():
    df = sector_engine.get_sector_summary()
    return df.to_dict(orient="records")

@app.get("/api/v1/sectors/{sector}/companies", tags=["Sector Analytics"])
def get_sector_companies(sector: str):
    return query_db("SELECT * FROM companies WHERE broad_sector = ?", (sector,))

@app.get("/api/v1/peers/{group_name}", tags=["Peer Analytics"])
def get_peer_group(group_name: str):
    df = peer_engine.get_peer_group_details(group_name)
    return df.to_dict(orient="records")

@app.get("/api/v1/companies/{ticker}/peers/compare", tags=["Peer Analytics"])
def compare_peer_company(ticker: str):
    conn = sqlite3.connect(DB_PATH)
    c_df = pd.read_sql_query("SELECT peer_group_name FROM peer_groups WHERE company_id = ?", conn, params=(ticker.upper(),))
    conn.close()
    if c_df.empty:
        raise HTTPException(status_code=404, detail=f"No peer group mapped for company {ticker}")
    p_name = c_df.iloc[0]["peer_group_name"]
    df = peer_engine.get_peer_group_details(p_name)
    return df.to_dict(orient="records")

@app.get("/api/v1/market-cap/{ticker}", tags=["Valuation"])
def get_market_cap(ticker: str):
    return query_db("SELECT * FROM market_cap WHERE company_id = ? ORDER BY year ASC", (ticker.upper(),))

@app.get("/api/v1/portfolio/stats", tags=["Portfolio Stats"])
def get_portfolio_stats():
    df = stats_engine.compute_percentile_distributions()
    return df.to_dict(orient="records")

@app.get("/api/v1/companies/{ticker}/documents", tags=["Documents Repository"])
def get_company_documents(ticker: str):
    return query_db("SELECT * FROM documents WHERE company_id = ? ORDER BY year DESC", (ticker.upper(),))
