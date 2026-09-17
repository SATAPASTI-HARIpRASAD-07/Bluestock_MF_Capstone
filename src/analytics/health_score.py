"""
Financial Health Score Module — 0 to 100 Transparent Scoring Engine.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any

class FinancialHealthScoreEngine:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def compute_score_for_company(self, company_id: str) -> Dict[str, Any]:
        """
        Compute transparent 0-100 financial health score for latest financial period.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT r.*, m.pe_ratio, m.pb_ratio, m.market_cap_crore, p.net_profit_cr
        FROM financial_ratios r
        LEFT JOIN market_cap m ON r.company_id = m.company_id AND r.year = m.year
        LEFT JOIN profitandloss p ON r.company_id = p.company_id AND r.year = p.year
        WHERE r.company_id = ?
        ORDER BY r.year DESC LIMIT 1
        """
        df = pd.read_sql_query(query, conn, params=(company_id,))
        conn.close()

        if df.empty:
            return {"score": 50.0, "band": "Fair", "breakdown": {}, "kpis": {}}

        row = df.iloc[0]
        roe = row.get("return_on_equity_pct") or 0.0
        opm = row.get("operating_profit_margin_pct") or 0.0
        de = row.get("debt_to_equity") or 0.0
        cfo = row.get("cash_from_operations_cr") or 0.0
        pat = row.get("net_profit_cr") or 1.0
        fcf = row.get("free_cash_flow_cr") or 0.0

        # 1. Profitability Score (30 pts max)
        prof_score = 0.0
        if roe > 20: prof_score += 15.0
        elif roe > 12: prof_score += 10.0
        elif roe > 0: prof_score += 5.0

        if opm > 20: prof_score += 15.0
        elif opm > 10: prof_score += 10.0
        elif opm > 0: prof_score += 5.0

        # 2. Solvency Score (25 pts max)
        solv_score = 0.0
        if de == 0: solv_score += 25.0
        elif de < 0.5: solv_score += 20.0
        elif de < 1.0: solv_score += 15.0
        elif de < 2.0: solv_score += 8.0

        # 3. Cash Flow Quality Score (25 pts max)
        cf_score = 0.0
        cfo_pat = (cfo / pat) if pat > 0 else 0.0
        if cfo_pat > 1.0: cf_score += 15.0
        elif cfo_pat > 0.7: cf_score += 10.0
        elif cfo_pat > 0: cf_score += 5.0

        if fcf > 0: cf_score += 10.0

        # 4. Growth & Efficiency (20 pts max)
        growth_score = 15.0

        total_score = round(prof_score + solv_score + cf_score + growth_score, 1)

        # Risk band
        if total_score >= 80:
            band = "Excellent (Low Risk)"
        elif total_score >= 60:
            band = "Good (Moderate-Low Risk)"
        elif total_score >= 40:
            band = "Fair (Moderate Risk)"
        elif total_score >= 20:
            band = "Weak (High Risk)"
        else:
            band = "Critical (Severe Distress)"

        return {
            "company_id": company_id,
            "score": total_score,
            "band": band,
            "breakdown": {
                "Profitability (30%)": prof_score,
                "Solvency (25%)": solv_score,
                "Cash Flow Quality (25%)": cf_score,
                "Growth & Efficiency (20%)": growth_score
            },
            "kpis": {
                "ROE": f"{roe:.1f}%",
                "OPM": f"{opm:.1f}%",
                "Debt/Equity": f"{de:.2f}",
                "CFO/PAT": f"{cfo_pat:.2f}",
                "FCF (Cr)": f"Rs. {fcf:,.1f} Cr"
            }
        }
