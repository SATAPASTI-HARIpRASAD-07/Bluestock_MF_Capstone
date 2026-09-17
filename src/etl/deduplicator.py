"""
Deduplicator Module for Nifty 100 Financial Datasets.
"""

import pandas as pd
from typing import List, Tuple

def deduplicate_dataset(df: pd.DataFrame, key_columns: List[str]) -> Tuple[pd.DataFrame, int]:
    """
    Remove duplicate records based on primary composite key columns.
    Returns clean DataFrame and count of removed duplicates.
    """
    initial_rows = len(df)
    clean_df = df.drop_duplicates(subset=key_columns, keep='last').copy()
    duplicates_removed = initial_rows - len(clean_df)
    return clean_df, duplicates_removed
