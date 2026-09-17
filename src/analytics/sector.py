"""
Sector Analytics Engine — Medians, Benchmarks, and Relative Analysis.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any

class SectorAnalyticsEngine:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def get_sector_summary(self) -> pd.DataFrame:
        """
        Calculate sector level medians for ROE, D/E, P/E, NPM, and Market Cap.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        WITH LatestYears AS (
            SELECT company_id, MAX(year) as max_year
            FROM financial_ratios
            GROUP BY company_id
        )
        SELECT s.broad_sector, r.company_id, r.return_on_equity_pct as roe,
               r.debt_to_equity as de, r.net_profit_margin_pct as npm,
               r.free_cash_flow_cr as fcf, m.pe_ratio as pe, m.market_cap_crore as mcap
        FROM sectors s
        JOIN LatestYears ly ON s.company_id = ly.company_id
        JOIN financial_ratios r ON r.company_id = ly.company_id AND r.year = ly.max_year
        LEFT JOIN market_cap m ON m.company_id = ly.company_id AND m.year = ly.max_year
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        sector_stats = df.groupby("broad_sector").agg(
            company_count=("company_id", "nunique"),
            median_roe=("roe", "median"),
            median_de=("de", "median"),
            median_npm=("npm", "median"),
            median_pe=("pe", "median"),
            total_fcf=("fcf", "sum"),
            total_mcap=("mcap", "sum")
        ).reset_index()

        return sector_stats.sort_values(by="total_mcap", ascending=False)

    def get_company_vs_sector(self, company_id: str) -> Dict[str, Any]:
        """
        Compare a single company against its broad sector medians.
        """
        conn = sqlite3.connect(self.db_path)
        sec_query = "SELECT broad_sector FROM sectors WHERE company_id = ?"
        sec_df = pd.read_sql_query(sec_query, conn, params=(company_id,))
        if sec_df.empty:
            conn.close()
            return {}

        sector_name = sec_df.iloc[0]["broad_sector"]

        comp_query = """
        SELECT r.company_id, r.return_on_equity_pct as roe, r.debt_to_equity as de,
               r.net_profit_margin_pct as npm, m.pe_ratio as pe
        FROM financial_ratios r
        LEFT JOIN market_cap m ON r.company_id = m.company_id AND r.year = m.year
        WHERE r.company_id = ? ORDER BY r.year DESC LIMIT 1
        """
        comp_df = pd.read_sql_query(comp_query, conn, params=(company_id,))

        sec_summary = self.get_sector_summary()
        sec_row = sec_summary[sec_summary["broad_sector"] == sector_name]
        conn.close()

        if comp_df.empty or sec_row.empty:
            return {}

        c = comp_df.iloc[0]
        s = sec_row.iloc[0]

        return {
            "company_id": company_id,
            "broad_sector": sector_name,
            "metrics": {
                "ROE": {"company": round(c["roe"], 2) if pd.notnull(c["roe"]) else 0.0, "sector_median": round(s["median_roe"], 2)},
                "Debt_to_Equity": {"company": round(c["de"], 2) if pd.notnull(c["de"]) else 0.0, "sector_median": round(s["median_de"], 2)},
                "NPM_Pct": {"company": round(c["npm"], 2) if pd.notnull(c["npm"]) else 0.0, "sector_median": round(s["median_npm"], 2)},
                "PE_Ratio": {"company": round(c["pe"], 2) if pd.notnull(c["pe"]) else 0.0, "sector_median": round(s["median_pe"], 2)}
            }
        }
