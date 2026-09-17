"""
Valuation Engine — Valuation Multiples, Percentile Bands, and Valuation Flags.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any

class ValuationEngine:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def get_company_valuation_trend(self, company_id: str) -> pd.DataFrame:
        """
        Fetch 6-year valuation trend for P/E, P/B, EV/EBITDA, Dividend Yield.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        SELECT year, market_cap_crore, enterprise_value_crore, pe_ratio, pb_ratio, ev_ebitda, dividend_yield_pct
        FROM market_cap
        WHERE company_id = ?
        ORDER BY year ASC
        """
        df = pd.read_sql_query(query, conn, params=(company_id,))
        conn.close()

        if not df.empty:
            # Historical P/E Percentile Bands
            pe_mean = df["pe_ratio"].mean()
            pe_std = df["pe_ratio"].std()
            df["pe_zscore"] = ((df["pe_ratio"] - pe_mean) / pe_std).round(2) if pe_std > 0 else 0.0

        return df

    def get_valuation_flag(self, company_id: str) -> Dict[str, Any]:
        """
        Generate valuation flag based on current P/E vs historical average.
        """
        df = self.get_company_valuation_trend(company_id)
        if df.empty:
            return {"company_id": company_id, "flag": "NO_VALUATION_DATA"}

        latest = df.iloc[-1]
        pe_curr = latest["pe_ratio"]
        pe_avg = df["pe_ratio"].mean()

        if pe_curr < pe_avg * 0.8:
            flag = "ATTRACTIVE_VALUATION"
            desc = f"Trading at P/E {pe_curr:.1f} vs 6-Yr Avg {pe_avg:.1f} (Discount)"
        elif pe_curr > pe_avg * 1.3:
            flag = "PREMIUM_VALUATION"
            desc = f"Trading at P/E {pe_curr:.1f} vs 6-Yr Avg {pe_avg:.1f} (Premium)"
        else:
            flag = "FAIR_VALUATION"
            desc = f"Trading at P/E {pe_curr:.1f} near 6-Yr Avg {pe_avg:.1f}"

        return {
            "company_id": company_id,
            "latest_pe": pe_curr,
            "historical_avg_pe": round(pe_avg, 1),
            "flag": flag,
            "description": desc
        }
