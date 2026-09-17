"""
Ticker and Year Normalization Module for Nifty 100 Financial Datasets.
"""

import re
from typing import Union

def normalize_ticker(ticker: Union[str, int, float]) -> str:
    """
    Standardize company ticker identifiers.
    Converts to string, strips whitespace, converts to uppercase.
    """
    if ticker is None or (isinstance(ticker, float) and str(ticker) == 'nan'):
        return ""
    return str(ticker).strip().upper()

def normalize_year(year_val: Union[str, int, float]) -> str:
    """
    Standardize year strings and period labels into clean financial year formats (e.g., FY24, FY23).
    Supports formats like 'Mar-24', 'Mar-2024', 'Dec 2023', '2024', 'FY24'.
    """
    if year_val is None or (isinstance(year_val, float) and str(year_val) == 'nan'):
        return "N/A"
    
    val_str = str(year_val).strip()
    
    # Check 4-digit pure year e.g. 2024
    if re.match(r'^\d{4}$', val_str):
        yy = val_str[2:]
        return f"FY{yy}"
    
    # Check FY format e.g. FY24 or FY2024
    match_fy = re.match(r'^FY\s*(\d{2,4})$', val_str, re.IGNORECASE)
    if match_fy:
        yy = match_fy.group(1)[-2:]
        return f"FY{yy}"

    # Check Month-Year format e.g. Mar-24, Mar-2024, Dec 23, Sep 2024
    match_my = re.search(r'([A-Za-z]{3})[-_\s]?(\d{2,4})', val_str)
    if match_my:
        year_part = match_my.group(2)
        yy = year_part[-2:]
        return f"FY{yy}"

    return val_str

def year_to_integer(year_label: str) -> int:
    """
    Convert FY label (e.g. FY24, 2024) to 4-digit integer (e.g. 2024).
    """
    norm = normalize_year(year_label)
    if norm.startswith("FY") and len(norm) == 4 and norm[2:].isdigit():
        yy = int(norm[2:])
        return 2000 + yy if yy < 50 else 1900 + yy
    try:
        return int(year_label)
    except Exception:
        return 2024
