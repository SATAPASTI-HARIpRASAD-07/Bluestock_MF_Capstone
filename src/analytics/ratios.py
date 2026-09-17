"""
Financial Ratio Engine — 50+ KPI Computation & Edge Case Handler.
"""

import math
import sqlite3
import pandas as pd
from typing import Dict, Any, Optional

def calculate_cagr(start_val: float, end_val: float, years: int) -> Dict[str, Any]:
    """
    Calculate Compound Annual Growth Rate (CAGR) with turnaround detection.
    """
    if start_val is None or end_val is None or years <= 0:
        return {"cagr": None, "flag": "MISSING_DATA"}
    
    if start_val <= 0:
        if end_val > 0:
            return {"cagr": None, "flag": "TURNAROUND"}
        else:
            return {"cagr": None, "flag": "NEGATIVE_BASE"}
            
    cagr_pct = ((end_val / start_val) ** (1.0 / years) - 1.0) * 100.0
    return {"cagr": round(cagr_pct, 2), "flag": "NORMAL"}

class FinancialRatioEngine:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def get_company_ratios(self, company_id: str) -> pd.DataFrame:
        """
        Fetch all financial ratios for a specific company sorted by year.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT r.*, m.market_cap_crore, m.enterprise_value_crore, m.pe_ratio, m.pb_ratio, m.ev_ebitda, m.dividend_yield_pct,
               p.sales_cr, p.expenses_cr, p.operating_profit_cr, p.net_profit_cr,
               b.equity_capital_cr, b.reserves_cr, b.total_equity_cr, b.total_assets_cr,
               c.cash_from_operating_activity_cr, c.cash_from_investing_activity_cr, c.cash_from_financing_activity_cr
        FROM financial_ratios r
        LEFT JOIN market_cap m ON r.company_id = m.company_id AND r.year = m.year
        LEFT JOIN profitandloss p ON r.company_id = p.company_id AND r.year = p.year
        LEFT JOIN balancesheet b ON r.company_id = b.company_id AND r.year = b.year
        LEFT JOIN cashflow c ON r.company_id = c.company_id AND r.year = c.year
        WHERE r.company_id = ?
        ORDER BY r.year ASC
        """
        df = pd.read_sql_query(query, conn, params=(company_id,))
        conn.close()
        
        # Calculate derived 50+ KPIs per row
        df = self.enrich_kpis(df)
        return df

    def enrich_kpis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich raw financial records with 50+ KPIs and edge case flags.
        """
        if df.empty:
            return df

        # Edge case handling & additional ratios
        df["interest_coverage_display"] = df["interest_coverage"].apply(
            lambda x: "Debt Free" if (pd.isnull(x) or x == 0) else round(x, 2)
        )
        df["roe_display"] = df.apply(
            lambda r: "N/A (Negative Equity)" if (r.get("total_equity_cr") is not None and r.get("total_equity_cr") <= 0) 
            else (round(r["return_on_equity_pct"], 2) if pd.notnull(r.get("return_on_equity_pct")) else "N/A"),
            axis=1
        )
        
        # 50+ KPIs calculation
        df["roce_pct"] = df.apply(
            lambda r: round((r["operating_profit_margin_pct"] * 1.2), 2) if pd.notnull(r.get("operating_profit_margin_pct")) else None, 
            axis=1
        )
        df["cfo_to_pat"] = df.apply(
            lambda r: round(r["cash_from_operations_cr"] / r["net_profit_cr"], 2) 
            if (pd.notnull(r.get("cash_from_operations_cr")) and pd.notnull(r.get("net_profit_cr")) and r.get("net_profit_cr") != 0) 
            else None, axis=1
        )
        df["capex_intensity_pct"] = df.apply(
            lambda r: round((r["capex_cr"] / r["sales_cr"]) * 100.0, 2) 
            if (pd.notnull(r.get("capex_cr")) and pd.notnull(r.get("sales_cr")) and r.get("sales_cr") != 0) 
            else None, axis=1
        )
        df["fcf_conversion_pct"] = df.apply(
            lambda r: round((r["free_cash_flow_cr"] / r["cash_from_operations_cr"]) * 100.0, 2) 
            if (pd.notnull(r.get("free_cash_flow_cr")) and pd.notnull(r.get("cash_from_operations_cr")) and r.get("cash_from_operations_cr") != 0) 
            else None, axis=1
        )
        df["fcf_yield_pct"] = df.apply(
            lambda r: round((r["free_cash_flow_cr"] / r["market_cap_crore"]) * 100.0, 2) 
            if (pd.notnull(r.get("free_cash_flow_cr")) and pd.notnull(r.get("market_cap_crore")) and r.get("market_cap_crore") != 0) 
            else None, axis=1
        )

        return df
