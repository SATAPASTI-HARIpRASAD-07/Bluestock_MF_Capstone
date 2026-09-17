import os
import pandas as pd
from src.etl.validator import DataQualityValidator

def test_data_quality_validator(tmp_path):
    validator = DataQualityValidator(output_dir=str(tmp_path))
    validator.log_failure("TEST", "FY24", "debt_to_equity", "Negative debt-to-equity ratio", "WARNING")
    validator.log_audit("test_dataset", 100, 95, 5, "PASS")
    validator.save_reports()

    assert os.path.exists(tmp_path / "validation_failures.csv")
    assert os.path.exists(tmp_path / "load_audit.csv")

    df_fail = pd.read_csv(tmp_path / "validation_failures.csv")
    assert len(df_fail) == 1
    assert df_fail.iloc[0]["company_id"] == "TEST"
