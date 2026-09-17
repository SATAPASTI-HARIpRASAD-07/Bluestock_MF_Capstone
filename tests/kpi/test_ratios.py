import pytest
from src.analytics.ratios import calculate_cagr

def test_calculate_cagr_normal():
    res = calculate_cagr(100.0, 121.0, 2)
    assert res["flag"] == "NORMAL"
    assert res["cagr"] == 10.0

def test_calculate_cagr_turnaround():
    res = calculate_cagr(-50.0, 100.0, 3)
    assert res["flag"] == "TURNAROUND"
    assert res["cagr"] is None

def test_calculate_cagr_zero_or_negative_end():
    res = calculate_cagr(-100.0, -50.0, 2)
    assert res["flag"] == "NEGATIVE_BASE"
    assert res["cagr"] is None
