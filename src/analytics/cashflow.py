"""
Cash Flow Intelligence Engine — CFO/PAT Quality, CapEx Intensity, and Capital Allocation Matrix.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, List

class CashFlowIntelligenceEngine:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def analyze_company_cashflow(self, company_id: str) -> Dict[str, Any]:
        """
        Analyze earnings quality, CapEx intensity, distress patterns, and capital allocation sign matrix.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT r.year, r.cash_from_operations_cr as cfo, r.capex_cr as capex, r.free_cash_flow_cr as fcf,
               r.total_debt_cr as total_debt, p.net_profit_cr as pat, p.sales_cr as sales,
               c.cash_from_investing_activity_cr as cfi, c.cash_from_financing_activity_cr as cff
        FROM financial_ratios r
        LEFT JOIN profitandloss p ON r.company_id = p.company_id AND r.year = p.year
        LEFT JOIN cashflow c ON r.company_id = c.company_id AND r.year = c.year
        WHERE r.company_id = ?
        ORDER BY r.year DESC LIMIT 1
        """
        df = pd.read_sql_query(query, conn, params=(company_id,))
        conn.close()

        if df.empty:
            return {"company_id": company_id, "status": "NO_DATA"}

        row = df.iloc[0]
        cfo = row.get("cfo") or 0.0
        pat = row.get("pat") or 1.0
        capex = row.get("capex") or 0.0
        sales = row.get("sales") or 1.0
        cfi = row.get("cfi") or 0.0
        cff = row.get("cff") or 0.0

        # CFO / PAT Earnings Quality
        cfo_pat = (cfo / pat) if pat > 0 else 0.0
        if cfo_pat >= 1.0:
            quality = "High Quality Earnings"
        elif cfo_pat >= 0.7:
            quality = "Normal Earnings Quality"
        else:
            quality = "Accrual Risk / Low Cash Conversion"

        # CapEx Intensity
        capex_intensity = (capex / sales * 100.0) if sales > 0 else 0.0
        if capex_intensity < 5.0:
            capex_class = "Asset Light"
        elif capex_intensity <= 15.0:
            capex_class = "Moderate CapEx"
        else:
            capex_class = "Capital Intensive"

        # Distress Pattern Detection
        is_distress = (cfo < 0 and cff > 0)

        # Capital Allocation Sign Matrix (8 patterns)
        s_cfo = "+" if cfo >= 0 else "-"
        s_cfi = "+" if cfi >= 0 else "-"
        s_cff = "+" if cff >= 0 else "-"
        pattern = f"{s_cfo}{s_cfi}{s_cff}"

        pattern_names = {
            "+-+": "Successful Growing Company (Reinvesting & Raising Capital)",
            "+--": "Mature Cash Generator (Investing & Repaying Debt/Dividends)",
            "++-": "Divesting & Paying Down Debt",
            "+++": "Exceptional Liquidity / Asset Sale & Debt Raising",
            "-++": "Turnaround / External Funding Dependent",
            "--+": "Distress / Borrowing to Fund Operations & CapEx",
            "-+-": "Asset Liquidation to Support Operations",
            "---": "Severe Distress / Cash Depletion"
        }
        pattern_desc = pattern_names.get(pattern, "Unclassified Cash Flow Pattern")

        return {
            "company_id": company_id,
            "year": row["year"],
            "cfo_pat_ratio": round(cfo_pat, 2),
            "earnings_quality": quality,
            "capex_intensity_pct": round(capex_intensity, 2),
            "capex_classification": capex_class,
            "distress_flag": is_distress,
            "sign_pattern": pattern,
            "pattern_description": pattern_desc
        }
