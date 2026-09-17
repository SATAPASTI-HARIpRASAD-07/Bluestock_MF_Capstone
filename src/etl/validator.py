"""
Data Quality Validation Engine for Nifty 100 Financial Intelligence Platform.
"""

import os
import pandas as pd
from typing import List, Dict, Any

class DataQualityValidator:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.failures: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []

    def log_failure(self, company_id: str, year: str, field: str, issue: str, severity: str):
        self.failures.append({
            "company_id": company_id,
            "year": year,
            "field": field,
            "issue": issue,
            "severity": severity
        })

    def log_audit(self, dataset_name: str, total_rows: int, valid_rows: int, duplicate_rows: int, status: str):
        self.audit_log.append({
            "dataset_name": dataset_name,
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "duplicate_rows": duplicate_rows,
            "status": status
        })

    def validate_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate financial ratios table constraints and arithmetic logic.
        """
        required_cols = ["company_id", "year", "net_profit_margin_pct", "return_on_equity_pct", "debt_to_equity"]
        for col in required_cols:
            if col not in df.columns:
                self.log_failure("GLOBAL", "ALL", col, f"Missing required column {col}", "CRITICAL")

        for idx, row in df.iterrows():
            cid = str(row.get("company_id", "UNKNOWN"))
            yr = str(row.get("year", "N/A"))

            # Check debt to equity negative
            de = row.get("debt_to_equity")
            if pd.notnull(de) and de < 0:
                self.log_failure(cid, yr, "debt_to_equity", f"Negative debt-to-equity ratio: {de}", "WARNING")

            # Check FCF = CFO - CapEx consistency
            cfo = row.get("cash_from_operations_cr")
            capex = row.get("capex_cr")
            fcf = row.get("free_cash_flow_cr")
            if pd.notnull(cfo) and pd.notnull(capex) and pd.notnull(fcf):
                expected_fcf = cfo - capex
                if abs(expected_fcf - fcf) > 5.0: # 5 Cr tolerance
                    self.log_failure(cid, yr, "free_cash_flow_cr", f"FCF mismatch: reported {fcf}, calculated {expected_fcf}", "INFO")

        return df

    def save_reports(self):
        """
        Export validation_failures.csv and load_audit.csv.
        """
        failures_df = pd.DataFrame(self.failures)
        if failures_df.empty:
            failures_df = pd.DataFrame(columns=["company_id", "year", "field", "issue", "severity"])
        failures_path = os.path.join(self.output_dir, "validation_failures.csv")
        failures_df.to_csv(failures_path, index=False)

        audit_df = pd.DataFrame(self.audit_log)
        if audit_df.empty:
            audit_df = pd.DataFrame(columns=["dataset_name", "total_rows", "valid_rows", "duplicate_rows", "status"])
        audit_path = os.path.join(self.output_dir, "load_audit.csv")
        audit_df.to_csv(audit_path, index=False)
