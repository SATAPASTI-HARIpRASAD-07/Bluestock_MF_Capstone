"""
Alerts Engine & Local Watchlist Manager.
"""

import os
import json
import sqlite3
import pandas as pd
from typing import Dict, Any, List

class AlertEngine:
    def __init__(self, db_path: str = "db/nifty100.db", watchlist_path: str = "config/watchlist.json"):
        self.db_path = db_path
        self.watchlist_path = watchlist_path

    def get_watchlist(self) -> List[str]:
        if os.path.exists(self.watchlist_path):
            with open(self.watchlist_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return ["HDFCBANK", "RELIANCE", "TCS", "INFY", "ICICIBANK"]

    def save_watchlist(self, watchlist: List[str]):
        os.makedirs(os.path.dirname(self.watchlist_path), exist_ok=True)
        with open(self.watchlist_path, 'w', encoding='utf-8') as f:
            json.dump(watchlist, f, indent=2)

    def evaluate_company_alerts(self, company_id: str) -> List[Dict[str, Any]]:
        """
        Evaluate rule-based alert conditions for a company across recent periods.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT r.year, r.return_on_equity_pct as roe, r.debt_to_equity as de,
               r.free_cash_flow_cr as fcf, p.sales_cr as sales, p.net_profit_cr as pat
        FROM financial_ratios r
        LEFT JOIN profitandloss p ON r.company_id = p.company_id AND r.year = p.year
        WHERE r.company_id = ?
        ORDER BY r.year DESC LIMIT 3
        """
        df = pd.read_sql_query(query, conn, params=(company_id,))
        conn.close()

        alerts = []
        if len(df) >= 2:
            latest = df.iloc[0]
            prev = df.iloc[1]

            # Alert 1: ROE Deterioration (> 3% drop)
            if pd.notnull(latest["roe"]) and pd.notnull(prev["roe"]):
                if prev["roe"] - latest["roe"] > 3.0:
                    alerts.append({
                        "type": "ROE_DETERIORATION",
                        "severity": "WARNING",
                        "message": f"ROE dropped by {prev['roe'] - latest['roe']:.1f}% from {prev['roe']:.1f}% to {latest['roe']:.1f}%"
                    })

            # Alert 2: Revenue Decline
            if pd.notnull(latest["sales"]) and pd.notnull(prev["sales"]):
                if latest["sales"] < prev["sales"]:
                    drop_pct = ((prev["sales"] - latest["sales"]) / prev["sales"]) * 100.0
                    alerts.append({
                        "type": "REVENUE_DECLINE",
                        "severity": "WARNING",
                        "message": f"Annual Revenue declined by {drop_pct:.1f}% YoY"
                    })

            # Alert 3: FCF Negative
            if pd.notnull(latest["fcf"]) and latest["fcf"] < 0:
                alerts.append({
                    "type": "NEGATIVE_FCF",
                    "severity": "HIGH",
                    "message": f"Free Cash Flow turned negative at Rs. {abs(latest['fcf']):,.1f} Cr"
                })

            # Alert 4: Debt-to-Equity Increase (> 0.3 increase)
            if pd.notnull(latest["de"]) and pd.notnull(prev["de"]):
                if latest["de"] - prev["de"] > 0.3:
                    alerts.append({
                        "type": "LEVERAGE_INCREASE",
                        "severity": "HIGH",
                        "message": f"Debt-to-Equity increased from {prev['de']:.2f} to {latest['de']:.2f}"
                    })

        return alerts
