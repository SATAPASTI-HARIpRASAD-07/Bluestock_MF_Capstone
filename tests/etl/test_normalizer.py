import pytest
from src.etl.normalizer import normalize_ticker, normalize_year, year_to_integer

def test_normalize_ticker():
    assert normalize_ticker(" hdfcbank ") == "HDFCBANK"
    assert normalize_ticker("abb") == "ABB"
    assert normalize_ticker(None) == ""

def test_normalize_year():
    assert normalize_year("Mar-24") == "FY24"
    assert normalize_year("Mar-2024") == "FY24"
    assert normalize_year("Dec 2023") == "FY23"
    assert normalize_year("2024") == "FY24"
    assert normalize_year("FY24") == "FY24"

def test_year_to_integer():
    assert year_to_integer("FY24") == 2024
    assert year_to_integer("FY23") == 2023
