"""
Portfolio Statistics, Correlation Analysis, and Outlier Detection Engine.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, Any

class PortfolioStatisticsEngine:
    def __init__(self, db_path: str = "db/nifty100.db", output_dir: str = "outputs"):
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_latest_metrics(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        query = """
        WITH LatestYears AS (
            SELECT company_id, MAX(year) as max_year
            FROM financial_ratios
            GROUP BY company_id
        )
        SELECT r.company_id, c.broad_sector, r.return_on_equity_pct as roe,
               r.debt_to_equity as de, r.net_profit_margin_pct as npm,
               r.operating_profit_margin_pct as opm, r.free_cash_flow_cr as fcf,
               m.pe_ratio as pe, m.pb_ratio as pb, m.market_cap_crore as mcap
        FROM financial_ratios r
        JOIN LatestYears ly ON r.company_id = ly.company_id AND r.year = ly.max_year
        JOIN companies c ON r.company_id = c.company_id
        LEFT JOIN market_cap m ON r.company_id = m.company_id AND r.year = m.year
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def compute_percentile_distributions(self) -> pd.DataFrame:
        """
        Calculate P10, P25, P50, P75, P90, Mean, Std across portfolio KPIs.
        """
        df = self.get_latest_metrics()
        num_cols = ["roe", "de", "npm", "opm", "fcf", "pe", "pb", "mcap"]
        stats = []

        for col in num_cols:
            series = df[col].dropna()
            stats.append({
                "metric": col,
                "mean": round(series.mean(), 2),
                "std": round(series.std(), 2),
                "P10": round(np.percentile(series, 10), 2),
                "P25": round(np.percentile(series, 25), 2),
                "P50": round(np.percentile(series, 50), 2),
                "P75": round(np.percentile(series, 75), 2),
                "P90": round(np.percentile(series, 90), 2)
            })

        return pd.DataFrame(stats)

    def compute_correlation_matrix(self) -> pd.DataFrame:
        """
        Compute Pearson correlation matrix across financial KPIs.
        """
        df = self.get_latest_metrics()
        num_cols = ["roe", "de", "npm", "opm", "fcf", "pe", "pb", "mcap"]
        return df[num_cols].corr().round(2)

    def detect_outliers(self) -> pd.DataFrame:
        """
        Perform sector-level Z-score analysis. Flag |Z| > 3 as outliers and save outputs/outlier_report.csv.
        """
        df = self.get_latest_metrics()
        outliers = []

        metrics = ["roe", "de", "npm", "opm", "pe"]
        for sector, grp in df.groupby("broad_sector"):
            if len(grp) < 3:
                continue
            for metric in metrics:
                mean = grp[metric].mean()
                std = grp[metric].std()
                if std > 0:
                    for _, row in grp.iterrows():
                        val = row[metric]
                        if pd.notnull(val):
                            z = (val - mean) / std
                            if abs(z) > 3.0:
                                outliers.append({
                                    "company_id": row["company_id"],
                                    "metric": metric,
                                    "value": round(val, 2),
                                    "z_score": round(z, 2),
                                    "sector": sector,
                                    "sector_mean": round(mean, 2),
                                    "sector_std": round(std, 2)
                                })

        outlier_df = pd.DataFrame(outliers)
        outlier_path = os.path.join(self.output_dir, "outlier_report.csv")
        outlier_df.to_csv(outlier_path, index=False)
        return outlier_df
