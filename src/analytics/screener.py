"""
Investment Screener Module supporting Preset and Custom Filters.
"""

import os
import yaml
import sqlite3
import pandas as pd
from typing import Dict, Any, List, Optional

class InvestmentScreener:
    def __init__(self, db_path: str = "db/nifty100.db", config_path: str = "config/screener_config.yaml"):
        self.db_path = db_path
        self.config_path = config_path
        self.presets = self._load_presets()

    def _load_presets(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get("presets", {})
        return {}

    def get_latest_universe(self) -> pd.DataFrame:
        """
        Fetch latest available year financial indicators for all 92 companies.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        WITH LatestYears AS (
            SELECT company_id, MAX(year) as max_year
            FROM financial_ratios
            GROUP BY company_id
        )
        SELECT c.company_id, c.company_name, c.broad_sector, c.sub_sector, c.market_cap_category,
               r.year, r.return_on_equity_pct as roe, r.debt_to_equity, r.free_cash_flow_cr as fcf,
               r.total_debt_cr as total_debt, r.net_profit_margin_pct as npm, r.operating_profit_margin_pct as opm,
               m.market_cap_crore, m.pe_ratio as pe, m.pb_ratio as pb, m.ev_ebitda, m.dividend_yield_pct as dividend_yield
        FROM companies c
        JOIN LatestYears ly ON c.company_id = ly.company_id
        JOIN financial_ratios r ON r.company_id = ly.company_id AND r.year = ly.max_year
        LEFT JOIN market_cap m ON m.company_id = ly.company_id AND m.year = ly.max_year
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def run_preset(self, preset_key: str) -> pd.DataFrame:
        """
        Run one of the preset screens (quality, value, growth, dividend, momentum, debt_free).
        """
        df = self.get_latest_universe()
        if preset_key not in self.presets:
            return df

        rules = self.presets[preset_key].get("rules", {})
        filtered = df.copy()

        if "min_roe" in rules and rules["min_roe"] is not None:
            filtered = filtered[filtered["roe"] >= rules["min_roe"]]
        if "max_debt_to_equity" in rules and rules["max_debt_to_equity"] is not None:
            filtered = filtered[filtered["debt_to_equity"] <= rules["max_debt_to_equity"]]
        if "min_free_cash_flow" in rules and rules["min_free_cash_flow"] is not None:
            filtered = filtered[filtered["fcf"] >= rules["min_free_cash_flow"]]
        if "max_pe" in rules and rules["max_pe"] is not None:
            filtered = filtered[(filtered["pe"] > 0) & (filtered["pe"] <= rules["max_pe"])]
        if "max_pb" in rules and rules["max_pb"] is not None:
            filtered = filtered[(filtered["pb"] > 0) & (filtered["pb"] <= rules["max_pb"])]
        if "min_dividend_yield" in rules and rules["min_dividend_yield"] is not None:
            filtered = filtered[filtered["dividend_yield"] >= rules["min_dividend_yield"]]
        if "max_total_debt" in rules and rules["max_total_debt"] is not None:
            filtered = filtered[filtered["total_debt"] <= rules["max_total_debt"]]

        return filtered.sort_values(by="market_cap_crore", ascending=False)

    def run_custom(self, min_roe: Optional[float] = None, max_de: Optional[float] = None,
                   min_fcf: Optional[float] = None, max_pe: Optional[float] = None,
                   sector: Optional[str] = None) -> pd.DataFrame:
        """
        Run custom multi-metric filter.
        """
        df = self.get_latest_universe()
        if sector and sector != "All":
            df = df[df["broad_sector"] == sector]
        if min_roe is not None:
            df = df[df["roe"] >= min_roe]
        if max_de is not None:
            df = df[df["debt_to_equity"] <= max_de]
        if min_fcf is not None:
            df = df[df["fcf"] >= min_fcf]
        if max_pe is not None:
            df = df[(df["pe"] > 0) & (df["pe"] <= max_pe)]

        return df.sort_values(by="market_cap_crore", ascending=False)
