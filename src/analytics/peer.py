"""
Peer Comparison Engine — Peer Groups, Percentile Ranks, and Benchmark Gaps.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, List

class PeerComparisonEngine:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def get_peer_groups(self) -> List[str]:
        """
        Get list of all defined peer group names.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT peer_group_name FROM peer_groups ORDER BY peer_group_name")
        groups = [r[0] for r in cursor.fetchall()]
        conn.close()
        return groups

    def get_peer_group_details(self, peer_group_name: str) -> pd.DataFrame:
        """
        Get all companies in a peer group with latest financial indicators and percentile ranks.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        WITH LatestYears AS (
            SELECT company_id, MAX(year) as max_year
            FROM financial_ratios
            GROUP BY company_id
        )
        SELECT p.peer_group_name, p.company_id, p.is_benchmark, c.company_name,
               r.return_on_equity_pct as roe, r.debt_to_equity as de,
               r.net_profit_margin_pct as npm, r.free_cash_flow_cr as fcf,
               m.pe_ratio as pe, m.market_cap_crore as mcap
        FROM peer_groups p
        JOIN companies c ON p.company_id = c.company_id
        JOIN LatestYears ly ON p.company_id = ly.company_id
        JOIN financial_ratios r ON r.company_id = ly.company_id AND r.year = ly.max_year
        LEFT JOIN market_cap m ON m.company_id = ly.company_id AND m.year = ly.max_year
        WHERE p.peer_group_name = ?
        """
        df = pd.read_sql_query(query, conn, params=(peer_group_name,))
        conn.close()

        if df.empty:
            return df

        # Calculate within-peer percentile ranks (0-100)
        df["roe_percentile"] = (df["roe"].rank(pct=True) * 100.0).round(1)
        df["fcf_percentile"] = (df["fcf"].rank(pct=True) * 100.0).round(1)
        df["npm_percentile"] = (df["npm"].rank(pct=True) * 100.0).round(1)

        return df.sort_values(by="mcap", ascending=False)
