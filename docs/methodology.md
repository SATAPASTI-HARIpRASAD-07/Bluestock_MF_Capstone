# Bluestock Nifty 100 Financial Intelligence — Methodology

## 1. Financial Health Score (0–100)

The Financial Health Score is an explainable, transparent 0 to 100 benchmark composed of four weighted categories:

1. **Profitability (30% weight)**:
   - ROE > 20%: 15 pts | ROE > 12%: 10 pts | ROE > 0%: 5 pts
   - OPM > 20%: 15 pts | OPM > 10%: 10 pts | OPM > 0%: 5 pts

2. **Solvency & Debt (25% weight)**:
   - Debt-to-Equity == 0: 25 pts | D/E < 0.5: 20 pts | D/E < 1.0: 15 pts | D/E < 2.0: 8 pts

3. **Cash Flow Quality (25% weight)**:
   - CFO / PAT > 1.0: 15 pts | CFO / PAT > 0.7: 10 pts | CFO / PAT > 0: 5 pts
   - Free Cash Flow > 0: 10 pts

4. **Growth & Operational Efficiency (20% weight)**:
   - Positive 3Y CAGR Revenue & Asset Turnover stability: 20 pts

### Risk Bands
- **80–100**: Excellent (Low Risk)
- **60–79**: Good (Moderate-Low Risk)
- **40–59**: Fair (Moderate Risk)
- **20–39**: Weak (High Risk)
- **0–19**: Critical (Severe Distress)

---

## 2. Edge Case Handling Rules

- **Zero Sales**: Denkominator returns `None` / `N/A`.
- **Zero Interest / Debt-Free**: Displayed as `Debt Free` (Coverage = `None`).
- **Negative Equity**: ROE returned as `N/A (Negative Equity)`.
- **CAGR Turnaround**: When base value is negative and ending value is positive, CAGR returns `None` with a `TURNAROUND` flag.
