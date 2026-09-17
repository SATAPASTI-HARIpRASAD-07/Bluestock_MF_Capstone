"""
Pros & Cons Generator — Automated Rule-Based Observation Engine.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, List

class ProsAndConsGenerator:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def generate_observations(self, company_id: str) -> Dict[str, Any]:
        """
        Generate rule-based pros and cons observations with confidence scores.
        """
        conn = sqlite3.connect(self.db_path)
        # Fetch supplied pros/cons
        p_query = "SELECT pros, cons FROM prosandcons WHERE company_id = ?"
        df_p = pd.read_sql_query(p_query, conn, params=(company_id,))

        # Fetch latest ratios
        r_query = """
        SELECT r.*, m.pb_ratio, m.pe_ratio
        FROM financial_ratios r
        LEFT JOIN market_cap m ON r.company_id = m.company_id AND r.year = m.year
        WHERE r.company_id = ?
        ORDER BY r.year DESC LIMIT 3
        """
        df_r = pd.read_sql_query(r_query, conn, params=(company_id,))
        conn.close()

        pros = []
        cons = []

        # Add supplied text if present
        if not df_p.empty:
            for _, r in df_p.iterrows():
                if pd.notnull(r.get("pros")) and str(r["pros"]).strip():
                    pros.append({"text": str(r["pros"]).strip(), "rule_triggered": "SUPPLIED_RECORD", "confidence": 1.0})
                if pd.notnull(r.get("cons")) and str(r["cons"]).strip():
                    cons.append({"text": str(r["cons"]).strip(), "rule_triggered": "SUPPLIED_RECORD", "confidence": 1.0})

        if not df_r.empty:
            latest = df_r.iloc[0]
            roe = latest.get("return_on_equity_pct") or 0.0
            de = latest.get("debt_to_equity") or 0.0
            fcf = latest.get("free_cash_flow_cr") or 0.0
            pb = latest.get("pb_ratio") or 0.0

            # Rule 1: High ROE
            if roe > 20.0:
                pros.append({"text": f"Company has a strong return on equity (ROE) of {roe:.1f}%.", "rule_triggered": "ROE > 20%", "confidence": 0.95})
            elif roe < 8.0:
                cons.append({"text": f"Company has a low return on equity (ROE) of {roe:.1f}%.", "rule_triggered": "ROE < 8%", "confidence": 0.90})

            # Rule 2: Debt-Free or Low Debt
            if de == 0:
                pros.append({"text": "Company is virtually debt-free with zero long-term borrowings.", "rule_triggered": "D/E == 0", "confidence": 0.98})
            elif de > 1.5:
                cons.append({"text": f"Company carries high financial leverage with Debt-to-Equity of {de:.2f}.", "rule_triggered": "D/E > 1.5", "confidence": 0.92})

            # Rule 3: Free Cash Flow
            if fcf > 1000.0:
                pros.append({"text": f"Strong cash generation with annual Free Cash Flow of Rs. {fcf:,.1f} Cr.", "rule_triggered": "FCF > 1000Cr", "confidence": 0.95})
            elif fcf < 0:
                cons.append({"text": f"Company reported negative Free Cash Flow of Rs. {abs(fcf):,.1f} Cr.", "rule_triggered": "FCF < 0", "confidence": 0.88})

            # Rule 4: Valuation Multiple
            if pb > 5.0:
                cons.append({"text": f"Stock is trading at a high price-to-book multiple of {pb:.2f}x.", "rule_triggered": "P/B > 5.0", "confidence": 0.85})

        return {
            "company_id": company_id,
            "pros": pros,
            "cons": cons
        }
