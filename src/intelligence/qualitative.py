"""
Qualitative Intelligence — CAGR Text Parser for Analysis Records.
"""

import re
import sqlite3
import pandas as pd
from typing import Dict, Any, List

def parse_cagr_text(text_val: str) -> Dict[str, float]:
    """
    Parse text strings like '10 Years: 21%', '5 Years: 6%', '3 Years: 15%' into key-value pairs.
    """
    if text_val is None or pd.isnull(text_val):
        return {}

    parsed = {}
    pattern = r'(\d+)\s*Years?:?\s*(-?\d+(?:\.\d+)?)\%'
    matches = re.findall(pattern, str(text_val), re.IGNORECASE)
    for period, val in matches:
        parsed[f"{period}Y"] = float(val)
    return parsed

class QualitativeTextParser:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def get_parsed_analysis(self, company_id: str) -> Dict[str, Any]:
        """
        Fetch qualitative compounding growth records for a company and parse into structured dict.
        """
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM analysis WHERE company_id = ?"
        df = pd.read_sql_query(query, conn, params=(company_id,))
        conn.close()

        if df.empty:
            return {"company_id": company_id, "has_records": False}

        row = df.iloc[0]
        return {
            "company_id": company_id,
            "has_records": True,
            "compounded_sales_growth": parse_cagr_text(row.get("compounded_sales_growth")),
            "compounded_profit_growth": parse_cagr_text(row.get("compounded_profit_growth")),
            "stock_price_cagr": parse_cagr_text(row.get("stock_price_cagr")),
            "roe_cagr": parse_cagr_text(row.get("roe"))
        }
