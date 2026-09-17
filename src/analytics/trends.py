"""
Trend & Growth Analytics Engine — Multi-Year CAGRs & Directional Indicators.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any
from src.analytics.ratios import calculate_cagr

class TrendAnalyticsEngine:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def compute_company_cagrs(self, company_id: str) -> Dict[str, Any]:
        """
        Compute 1Y, 3Y, 5Y, 10Y CAGRs for Revenue, PAT, EPS, and FCF for a given company.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT r.year, p.sales_cr, p.net_profit_cr, r.earnings_per_share as eps, r.free_cash_flow_cr as fcf
        FROM financial_ratios r
        LEFT JOIN profitandloss p ON r.company_id = p.company_id AND r.year = p.year
        WHERE r.company_id = ?
        ORDER BY r.year ASC
        """
        df = pd.read_sql_query(query, conn, params=(company_id,))
        conn.close()

        if df.empty or len(df) < 2:
            return {"company_id": company_id, "status": "INSUFFICIENT_DATA"}

        latest = df.iloc[-1]
        results = {"company_id": company_id, "latest_year": latest["year"]}

        # Helper for CAGR lookup
        def get_period_cagr(col_name: str, years: int):
            if len(df) <= years:
                return {"cagr": None, "flag": "INSUFFICIENT_HISTORY"}
            start_row = df.iloc[-(years + 1)]
            return calculate_cagr(start_row[col_name], latest[col_name], years)

        for metric in ["sales_cr", "net_profit_cr", "eps", "fcf"]:
            results[f"{metric}_cagr_3y"] = get_period_cagr(metric, 3)
            results[f"{metric}_cagr_5y"] = get_period_cagr(metric, 5)

        return results
