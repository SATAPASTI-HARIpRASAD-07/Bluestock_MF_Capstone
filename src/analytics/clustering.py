"""
Statistical Clustering Module — KMeans Clustering on Nifty 100 Companies.
"""

import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any

class StatisticalClusteringEngine:
    def __init__(self, db_path: str = "db/nifty100.db"):
        self.db_path = db_path

    def run_kmeans_clustering(self, n_clusters: int = 5) -> pd.DataFrame:
        """
        Standardize financial metrics (ROE, D/E, OPM, NPM, FCF) and perform KMeans clustering.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
        WITH LatestYears AS (
            SELECT company_id, MAX(year) as max_year
            FROM financial_ratios
            GROUP BY company_id
        )
        SELECT r.company_id, c.broad_sector, r.return_on_equity_pct as roe,
               r.debt_to_equity as de, r.operating_profit_margin_pct as opm,
               r.net_profit_margin_pct as npm, r.free_cash_flow_cr as fcf
        FROM financial_ratios r
        JOIN LatestYears ly ON r.company_id = ly.company_id AND r.year = ly.max_year
        JOIN companies c ON r.company_id = c.company_id
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return df

        features = ["roe", "de", "opm", "npm"]
        df_clean = df.dropna(subset=features).copy()

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_clean[features])

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_clean["cluster_id"] = kmeans.fit_predict(X_scaled)

        # Assign descriptive cluster labels
        cluster_labels = {
            0: "High Profitability Leaders",
            1: "Conservative Debt-Free Quality",
            2: "Capital Intensive / High Debt",
            3: "Moderate Growth Compounders",
            4: "Turnaround / Low Margin Entities"
        }
        df_clean["cluster_name"] = df_clean["cluster_id"].map(lambda c: cluster_labels.get(c, f"Cluster {c}"))

        return df_clean
