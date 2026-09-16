from flask import Flask, jsonify, render_template_string, request
import json
from pathlib import Path
import os
import pandas as pd

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

def load_processed_csv(filename):
    p = PROCESSED_DIR / filename
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()

def load_output_csv(filename):
    p = OUTPUT_DIR / filename
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "Bluestock Mutual Fund Analytics Platform", "version": "1.0"})

@app.route("/api/summary")
def summary_api():
    df_sip = load_processed_csv("04_monthly_sip_inflows.csv")
    df_folio = load_processed_csv("06_industry_folio_count.csv")
    df_master = load_processed_csv("01_fund_master.csv")
    
    latest_sip = df_sip.sort_values("month").iloc[-1].to_dict() if not df_sip.empty else {}
    latest_folio = df_folio.sort_values("month").iloc[-1].to_dict() if not df_folio.empty else {}
    
    return jsonify({
        "total_industry_aum_lakh_cr": 81.0,
        "top10_amc_aum_lakh_cr": 62.74,
        "latest_monthly_sip_inflow_cr": latest_sip.get("sip_inflow_crore", 31002),
        "sip_yoy_growth_pct": latest_sip.get("yoy_growth_pct", 17.17),
        "total_folio_count_cr": latest_folio.get("total_folios_crore", 26.12),
        "industry_schemes_count": 1908,
        "schemes_analyzed_count": len(df_master) if not df_master.empty else 40
    })

@app.route("/api/funds")
def funds_api():
    df_sc = load_output_csv("fund_scorecard.csv")
    if df_sc.empty:
        df_sc = load_processed_csv("07_scheme_performance.csv")
    return jsonify(df_sc.fillna("").to_dict(orient="records"))

@app.route("/api/recommend")
def recommend_api():
    risk = request.args.get("risk", "Moderate").strip().title()
    df_perf = load_processed_csv("07_scheme_performance.csv")
    if df_perf.empty:
        return jsonify([])
    
    if risk == "Low":
        allowed = ["Low", "Low to Moderate", "Moderate", "Debt", "Liquid", "Hybrid", "Large Cap"]
    elif risk == "High":
        allowed = ["High", "Very High", "Small Cap", "Mid Cap", "Equity", "Flexi Cap"]
    else:
        allowed = ["Moderate", "Moderately High", "Low to Moderate"]
        
    filtered = df_perf[(df_perf["risk_grade"].isin(allowed)) | (df_perf["category"].isin(allowed))]
    if filtered.empty:
        filtered = df_perf.copy()
        
    recommended = filtered.sort_values(by=["sharpe_ratio", "return_3yr_pct"], ascending=[False, False]).head(3)
    return jsonify(recommended.fillna("").to_dict(orient="records"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bluestock Mutual Fund Analytics Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --primary-color: #1e3a8a; --accent-color: #4f46e5; }
        body { background-color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); }
        .kpi-card { background: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-left: 5px solid var(--primary-color); transition: transform 0.2s; }
        .kpi-card:hover { transform: translateY(-3px); }
        .kpi-title { font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .kpi-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; margin-top: 5px; }
        .kpi-sub { font-size: 0.8rem; color: #10b981; font-weight: 600; margin-top: 5px; }
        .card-custom { background: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); padding: 24px; margin-bottom: 24px; border: 1px solid #e2e8f0; }
        .nav-tabs .nav-link.active { font-weight: bold; color: var(--primary-color); border-bottom: 3px solid var(--primary-color); }
        .table-responsive { max-height: 450px; overflow-y: auto; }
        .badge-risk { font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; }
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg navbar-dark shadow-sm mb-4">
        <div class="container-fluid px-4">
            <a class="navbar-brand fw-bold fs-4" href="#">
                📊 Bluestock Mutual Fund Analytics
            </a>
            <span class="navbar-text text-white-50">
                Capstone Analytics & Intelligence Platform
            </span>
        </div>
    </nav>

    <div class="container-fluid px-4">

        <!-- Top KPI Header Banner -->
        <div class="row g-3 mb-4">
            <div class="col-md-2.4 col-sm-6">
                <div class="kpi-card">
                    <div class="kpi-title">Total Industry AUM</div>
                    <div class="kpi-value">₹81.00 Lakh Cr</div>
                    <div class="kpi-sub">Top 10 AMCs: ₹62.74 Lakh Cr</div>
                </div>
            </div>
            <div class="col-md-2.4 col-sm-6">
                <div class="kpi-card" style="border-left-color: #10b981;">
                    <div class="kpi-title">Monthly SIP Inflow</div>
                    <div class="kpi-value">₹31,002 Cr</div>
                    <div class="kpi-sub">+17.17% YoY Growth</div>
                </div>
            </div>
            <div class="col-md-2.4 col-sm-6">
                <div class="kpi-card" style="border-left-color: #8b5cf6;">
                    <div class="kpi-title">Total Folio Count</div>
                    <div class="kpi-value">26.12 Cr</div>
                    <div class="kpi-sub">Retail Equity Driven</div>
                </div>
            </div>
            <div class="col-md-2.4 col-sm-6">
                <div class="kpi-card" style="border-left-color: #f59e0b;">
                    <div class="kpi-title">Industry Schemes</div>
                    <div class="kpi-value">1,908</div>
                    <div class="kpi-sub">Active SEBI Registered</div>
                </div>
            </div>
            <div class="col-md-2.4 col-sm-6">
                <div class="kpi-card" style="border-left-color: #06b6d4;">
                    <div class="kpi-title">Schemes Analyzed</div>
                    <div class="kpi-value">40</div>
                    <div class="kpi-sub">Capstone Sample Scope</div>
                </div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs mb-4" id="analyticsTabs" role="tablist">
            <li class="nav-item">
                <button class="nav-link active" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview" type="button">🏛️ Page 1: Industry Overview</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="performance-tab" data-bs-toggle="tab" data-bs-target="#performance" type="button">🏆 Page 2: Fund Performance & Scorecard</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="investor-tab" data-bs-toggle="tab" data-bs-target="#investor" type="button">👥 Page 3: Investor Analytics</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="trends-tab" data-bs-toggle="tab" data-bs-target="#trends" type="button">📈 Page 4: SIP & Market Trends</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="recommender-tab" data-bs-toggle="tab" data-bs-target="#recommender" type="button">🤖 Fund Recommender</button>
            </li>
        </ul>

        <!-- Tab Contents -->
        <div class="tab-content" id="analyticsTabsContent">

            <!-- PAGE 1: INDUSTRY OVERVIEW -->
            <div class="tab-pane fade show active" id="overview" role="tabpanel">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card-custom">
                            <h5 class="fw-bold text-dark mb-3">Industry AUM Trajectory (INR Cr)</h5>
                            <canvas id="aumChart" height="220"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card-custom">
                            <h5 class="fw-bold text-dark mb-3">Top 10 Fund Houses by AUM (INR Cr)</h5>
                            <canvas id="fundHouseChart" height="220"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PAGE 2: FUND PERFORMANCE & SCORECARD -->
            <div class="tab-pane fade" id="performance" role="tabpanel">
                <div class="card-custom">
                    <h5 class="fw-bold text-dark mb-3">Composite Mutual Fund Scorecard & Risk-Adjusted Metrics</h5>
                    <div class="table-responsive">
                        <table class="table table-hover table-striped align-middle">
                            <thead class="table-dark">
                                <tr>
                                    <th>Rank</th>
                                    <th>Scheme Name</th>
                                    <th>Category</th>
                                    <th>3Yr Return (%)</th>
                                    <th>Sharpe Ratio</th>
                                    <th>Alpha</th>
                                    <th>Beta</th>
                                    <th>Expense Ratio (%)</th>
                                    <th>Max Drawdown (%)</th>
                                    <th>Composite Score</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for fund in funds %}
                                <tr>
                                    <td><span class="badge bg-primary fs-6">{{ loop.index }}</span></td>
                                    <td class="fw-bold">{{ fund.scheme_name }}</td>
                                    <td><span class="badge bg-secondary">{{ fund.category }}</span></td>
                                    <td class="text-success fw-bold">{{ fund.return_3yr_pct }}%</td>
                                    <td>{{ fund.sharpe_ratio }}</td>
                                    <td>{{ fund.alpha }}</td>
                                    <td>{{ fund.beta }}</td>
                                    <td>{{ fund.expense_ratio_pct }}%</td>
                                    <td class="text-danger">{{ fund.max_drawdown_pct }}%</td>
                                    <td><span class="badge bg-success fs-6">{{ fund.composite_score if fund.composite_score else 'N/A' }}</span></td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- PAGE 3: INVESTOR ANALYTICS -->
            <div class="tab-pane fade" id="investor" role="tabpanel">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card-custom">
                            <h5 class="fw-bold text-dark mb-3">Top 10 States by Investor Transaction Volume (Cr)</h5>
                            <canvas id="stateChart" height="220"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card-custom">
                            <h5 class="fw-bold text-dark mb-3">Transaction Type Volume Split (Cr)</h5>
                            <canvas id="typeChart" height="220"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PAGE 4: SIP & MARKET TRENDS -->
            <div class="tab-pane fade" id="trends" role="tabpanel">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card-custom">
                            <h5 class="fw-bold text-dark mb-3">Monthly Industry SIP Inflow Trend (INR Cr)</h5>
                            <canvas id="sipTrendChart" height="220"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card-custom">
                            <h5 class="fw-bold text-dark mb-3">Category Net Inflow Distribution (INR Cr)</h5>
                            <canvas id="catInflowChart" height="220"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- RECOMMENDER TAB -->
            <div class="tab-pane fade" id="recommender" role="tabpanel">
                <div class="card-custom">
                    <h5 class="fw-bold text-dark mb-2">🤖 Transparent Rule-Based Fund Recommendation Engine</h5>
                    <p class="text-muted small">Select your risk tolerance profile to view top-matching mutual fund selections based on Sharpe Ratio and historical 3-year returns.</p>
                    
                    <div class="row align-items-center mb-4">
                        <div class="col-md-4">
                            <label class="form-label fw-bold">Select Risk Profile:</label>
                            <select id="riskSelect" class="form-select" onchange="fetchRecommendation()">
                                <option value="Low">Low Risk (Debt, Liquid, Conservative)</option>
                                <option value="Moderate" selected>Moderate Risk (Balanced, Hybrid, Large Cap)</option>
                                <option value="High">High Risk (Small Cap, Mid Cap, Aggressive Equity)</option>
                            </select>
                        </div>
                    </div>

                    <div id="recResults" class="row g-3">
                        <!-- Recommendation Cards Rendered via JS -->
                    </div>

                    <div class="alert alert-warning mt-4 small" role="alert">
                        ⚠️ <strong>EDUCATIONAL DISCLAIMER:</strong> This recommendation model is built strictly for academic and project capstone evaluation purposes. It does NOT constitute professional financial or investment advice.
                    </div>
                </div>
            </div>

        </div>

        <footer class="mt-5 py-3 text-center text-muted border-top">
            <p class="mb-0">Bluestock Mutual Fund Analytics Capstone Project | Deployed on Vercel</p>
        </footer>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Data passed from Flask backend
        const aumDates = {{ aum_dates|safe }};
        const aumValues = {{ aum_values|safe }};
        const fhNames = {{ fh_names|safe }};
        const fhAum = {{ fh_aum|safe }};
        const sipMonths = {{ sip_months|safe }};
        const sipInflows = {{ sip_inflows|safe }};
        const stateNames = {{ state_names|safe }};
        const stateVolumes = {{ state_volumes|safe }};
        const catNames = {{ cat_names|safe }};
        const catInflows = {{ cat_inflows|safe }};

        // Render Chart.js Visualizations
        window.addEventListener('DOMContentLoaded', () => {
            // 1. AUM Trajectory
            new Chart(document.getElementById('aumChart'), {
                type: 'line',
                data: { labels: aumDates, datasets: [{ label: 'Industry AUM (Cr)', data: aumValues, borderColor: '#1e3a8a', backgroundColor: 'rgba(30,58,138,0.1)', fill: true, tension: 0.3 }] },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });

            // 2. Fund House AUM
            new Chart(document.getElementById('fundHouseChart'), {
                type: 'bar',
                data: { labels: fhNames, datasets: [{ label: 'AUM (Cr)', data: fhAum, backgroundColor: '#3b82f6' }] },
                options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } } }
            });

            // 3. State Volume
            new Chart(document.getElementById('stateChart'), {
                type: 'bar',
                data: { labels: stateNames, datasets: [{ label: 'Volume (Cr)', data: stateVolumes, backgroundColor: '#10b981' }] },
                options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } } }
            });

            // 4. Transaction Type Split
            new Chart(document.getElementById('typeChart'), {
                type: 'doughnut',
                data: { labels: ['SIP', 'Lumpsum', 'Redemption'], datasets: [{ data: [1680.5, 950.2, 530.1], backgroundColor: ['#10b981', '#3b82f6', '#ef4444'] }] },
                options: { responsive: true }
            });

            // 5. SIP Inflow Trend
            new Chart(document.getElementById('sipTrendChart'), {
                type: 'line',
                data: { labels: sipMonths, datasets: [{ label: 'SIP Inflow (Cr)', data: sipInflows, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', fill: true, tension: 0.3 }] },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });

            // 6. Category Net Inflow
            new Chart(document.getElementById('catInflowChart'), {
                type: 'bar',
                data: { labels: catNames, datasets: [{ label: 'Net Inflow (Cr)', data: catInflows, backgroundColor: '#8b5cf6' }] },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });

            fetchRecommendation();
        });

        function fetchRecommendation() {
            const risk = document.getElementById('riskSelect').value;
            fetch('/api/recommend?risk=' + risk)
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('recResults');
                    container.innerHTML = '';
                    data.forEach((fund, idx) => {
                        container.innerHTML += `
                            <div class="col-md-4">
                                <div class="card h-100 border-primary shadow-sm">
                                    <div class="card-header bg-primary text-white fw-bold">
                                        Top Match #${idx + 1} — ${fund.scheme_name}
                                    </div>
                                    <div class="card-body">
                                        <p class="mb-1"><strong>Category:</strong> <span class="badge bg-secondary">${fund.category}</span></p>
                                        <p class="mb-1"><strong>Fund House:</strong> ${fund.fund_house}</p>
                                        <p class="mb-1 text-success"><strong>3Yr CAGR Return:</strong> ${fund.return_3yr_pct}%</p>
                                        <p class="mb-1"><strong>Sharpe Ratio:</strong> ${fund.sharpe_ratio}</p>
                                        <p class="mb-1"><strong>Expense Ratio:</strong> ${fund.expense_ratio_pct}%</p>
                                        <p class="mb-0"><strong>Risk Grade:</strong> ${fund.risk_grade}</p>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    df_sc = load_output_csv("fund_scorecard.csv")
    if df_sc.empty:
        df_sc = load_processed_csv("07_scheme_performance.csv")
    funds = df_sc.head(15).fillna("").to_dict(orient="records")
    
    df_aum = load_processed_csv("03_aum_by_fund_house.csv")
    aum_dates, aum_values, fh_names, fh_aum = [], [], [], []
    if not df_aum.empty:
        aum_trend = df_aum.groupby("date")["aum_crore"].sum().reset_index()
        aum_dates = aum_trend["date"].tolist()
        aum_values = aum_trend["aum_crore"].tolist()
        
        fh_summary = df_aum.groupby("fund_house")["aum_crore"].mean().sort_values(ascending=False).head(10)
        fh_names = fh_summary.index.tolist()
        fh_aum = fh_summary.values.tolist()
        
    df_sip = load_processed_csv("04_monthly_sip_inflows.csv")
    sip_months, sip_inflows = [], []
    if not df_sip.empty:
        sip_sorted = df_sip.sort_values("month")
        sip_months = sip_sorted["month"].tolist()
        sip_inflows = sip_sorted["sip_inflow_crore"].tolist()
        
    df_tx = load_processed_csv("08_investor_transactions.csv")
    state_names, state_volumes = [], []
    if not df_tx.empty:
        state_sum = (df_tx.groupby("state")["amount_inr"].sum().sort_values(ascending=False).head(10) / 1e7).round(2)
        state_names = state_sum.index.tolist()
        state_volumes = state_sum.values.tolist()
        
    df_cat = load_processed_csv("05_category_inflows.csv")
    cat_names, cat_inflows = [], []
    if not df_cat.empty:
        cat_sum = df_cat.groupby("category")["net_inflow_crore"].sum().sort_values(ascending=False).head(8).round(2)
        cat_names = cat_sum.index.tolist()
        cat_inflows = cat_sum.values.tolist()

    return render_template_string(
        HTML_TEMPLATE,
        funds=funds,
        aum_dates=json.dumps(aum_dates),
        aum_values=json.dumps(aum_values),
        fh_names=json.dumps(fh_names),
        fh_aum=json.dumps(fh_aum),
        sip_months=json.dumps(sip_months),
        sip_inflows=json.dumps(sip_inflows),
        state_names=json.dumps(state_names),
        state_volumes=json.dumps(state_volumes),
        cat_names=json.dumps(cat_names),
        cat_inflows=json.dumps(cat_inflows)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
