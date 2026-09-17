"""
Master Data Loader and Ingestion Pipeline for Nifty 100 Datasets.
"""

import os
import pandas as pd
from typing import Dict
from src.etl.normalizer import normalize_ticker, normalize_year
from src.etl.deduplicator import deduplicate_dataset
from src.etl.validator import DataQualityValidator

class MasterDataLoader:
    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = raw_dir
        self.validator = DataQualityValidator()

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """
        Load, normalize, validate, and deduplicate all raw Excel datasets.
        Returns dictionary of clean DataFrames keyed by dataset name.
        """
        datasets = {}

        # 1. sectors.xlsx (header=0)
        sectors_path = os.path.join(self.raw_dir, "sectors.xlsx")
        if os.path.exists(sectors_path):
            df_sec = pd.read_excel(sectors_path, header=0)
            df_sec["company_id"] = df_sec["company_id"].apply(normalize_ticker)
            df_sec, dup_cnt = deduplicate_dataset(df_sec, ["company_id"])
            self.validator.log_audit("sectors", len(df_sec) + dup_cnt, len(df_sec), dup_cnt, "PASS")
            datasets["sectors"] = df_sec

        # 2. peer_groups.xlsx (header=0)
        peer_path = os.path.join(self.raw_dir, "peer_groups.xlsx")
        if os.path.exists(peer_path):
            df_peer = pd.read_excel(peer_path, header=0)
            df_peer["company_id"] = df_peer["company_id"].apply(normalize_ticker)
            df_peer, dup_cnt = deduplicate_dataset(df_peer, ["peer_group_name", "company_id"])
            self.validator.log_audit("peer_groups", len(df_peer) + dup_cnt, len(df_peer), dup_cnt, "PASS")
            datasets["peer_groups"] = df_peer

        # 3. financial_ratios.xlsx (header=0)
        ratios_path = os.path.join(self.raw_dir, "financial_ratios.xlsx")
        if os.path.exists(ratios_path):
            df_rat = pd.read_excel(ratios_path, header=0)
            df_rat["company_id"] = df_rat["company_id"].apply(normalize_ticker)
            df_rat["year_label"] = df_rat["year"].astype(str)
            df_rat["year"] = df_rat["year"].apply(normalize_year)
            df_rat = self.validator.validate_ratios(df_rat)
            df_rat, dup_cnt = deduplicate_dataset(df_rat, ["company_id", "year"])
            self.validator.log_audit("financial_ratios", len(df_rat) + dup_cnt, len(df_rat), dup_cnt, "PASS")
            datasets["financial_ratios"] = df_rat

        # 4. market_cap.xlsx (header=0)
        mcap_path = os.path.join(self.raw_dir, "market_cap.xlsx")
        if os.path.exists(mcap_path):
            df_mcap = pd.read_excel(mcap_path, header=0)
            df_mcap["company_id"] = df_mcap["company_id"].apply(normalize_ticker)
            df_mcap["year"] = df_mcap["year"].apply(normalize_year)
            df_mcap, dup_cnt = deduplicate_dataset(df_mcap, ["company_id", "year"])
            self.validator.log_audit("market_cap", len(df_mcap) + dup_cnt, len(df_mcap), dup_cnt, "PASS")
            datasets["market_cap"] = df_mcap

        # 5. stock_prices.xlsx (header=0)
        prices_path = os.path.join(self.raw_dir, "stock_prices.xlsx")
        if os.path.exists(prices_path):
            df_prices = pd.read_excel(prices_path, header=0)
            df_prices["company_id"] = df_prices["company_id"].apply(normalize_ticker)
            df_prices["date"] = pd.to_datetime(df_prices["date"]).dt.strftime("%Y-%m-%d")
            df_prices, dup_cnt = deduplicate_dataset(df_prices, ["company_id", "date"])
            self.validator.log_audit("stock_prices", len(df_prices) + dup_cnt, len(df_prices), dup_cnt, "PASS")
            datasets["stock_prices"] = df_prices

        # 6. analysis.xlsx (header=1)
        analysis_path = os.path.join(self.raw_dir, "analysis.xlsx")
        if os.path.exists(analysis_path):
            df_ana = pd.read_excel(analysis_path, header=1)
            df_ana["company_id"] = df_ana["company_id"].apply(normalize_ticker)
            self.validator.log_audit("analysis", len(df_ana), len(df_ana), 0, "PASS")
            datasets["analysis"] = df_ana

        # 7. prosandcons.xlsx (header=1)
        pros_path = os.path.join(self.raw_dir, "prosandcons.xlsx")
        if os.path.exists(pros_path):
            df_pro = pd.read_excel(pros_path, header=1)
            df_pro["company_id"] = df_pro["company_id"].apply(normalize_ticker)
            self.validator.log_audit("prosandcons", len(df_pro), len(df_pro), 0, "PASS")
            datasets["prosandcons"] = df_pro

        # Save audit logs
        self.validator.save_reports()
        return datasets
