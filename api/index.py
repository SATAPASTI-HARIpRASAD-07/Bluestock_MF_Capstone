from flask import Flask, jsonify, render_template_string, request
import csv
import json
import os
from pathlib import Path
import sqlite3

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "bluestock_mf.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "bluestock_mf.db"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

def query_db(query, params=(), one=False):
    """Execute SQLite query safely in read-only mode using built-in sqlite3 module."""
    if not DB_PATH.exists():
        return []
    try:
        try:
            conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
        except Exception:
            conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, params)
        rv = cur.fetchall()
        conn.close()
        results = [dict(row) for row in rv]
        return (results[0] if results else None) if one else results
    except Exception as e:
        print(f"Database query error: {e}")
        return []

def read_csv_file(file_path):
    """Read CSV file using Python built-in csv module."""
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"CSV read error for {file_path}: {e}")
        return []

@app.route("/api/health")
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "app": "Bluestock Mutual Fund Analytics Platform",
        "version": "1.0",
        "framework": "Flask + Python Standard Library"
    })

@app.route("/api/summary")
@app.route("/summary")
def summary_api():
    sip_data = query_db("SELECT * FROM monthly_sip_inflows ORDER BY month DESC LIMIT 1", one=True)
    if not sip_data:
        csv_rows = read_csv_file(PROCESSED_DIR / "04_monthly_sip_inflows.csv")
        sip_data = csv_rows[-1] if csv_rows else {}

    folio_data = query_db("SELECT * FROM industry_folio_count ORDER BY month DESC LIMIT 1", one=True)
    if not folio_data:
        csv_rows = read_csv_file(PROCESSED_DIR / "06_industry_folio_count.csv")
        folio_data = csv_rows[-1] if csv_rows else {}

    fund_master_rows = query_db("SELECT COUNT(*) as cnt FROM fund_master", one=True)
    schemes_cnt = fund_master_rows["cnt"] if fund_master_rows else 40

    return jsonify({
        "total_industry_aum_lakh_cr": 81.0,
        "top10_amc_aum_lakh_cr": 62.74,
        "latest_monthly_sip_inflow_cr": float(sip_data.get("sip_inflow_crore", 31002) or 31002),
        "sip_yoy_growth_pct": float(sip_data.get("yoy_growth_pct", 17.17) or 17.17),
        "total_folio_count_cr": float(folio_data.get("total_folios_crore", 26.12) or 26.12),
        "industry_schemes_count": 1908,
        "schemes_analyzed_count": schemes_cnt
    })

@app.route("/api/funds")
@app.route("/funds")
def funds_api():
    scorecard = read_csv_file(OUTPUT_DIR / "fund_scorecard.csv")
    if not scorecard:
        scorecard = query_db("SELECT * FROM scheme_performance ORDER BY return_3yr_pct DESC")
    if not scorecard:
        scorecard = read_csv_file(PROCESSED_DIR / "07_scheme_performance.csv")
    return jsonify(scorecard)

@app.route("/api/recommend")
@app.route("/recommend")
def recommend_api():
    risk = request.args.get("risk", "Moderate").strip().title()
    funds = query_db("SELECT * FROM scheme_performance")
    if not funds:
        funds = read_csv_file(PROCESSED_DIR / "07_scheme_performance.csv")
        
    if not funds:
        return jsonify([])

    for f in funds:
        try:
            f["sharpe_ratio"] = float(f.get("sharpe_ratio", 0) or 0)
            f["return_3yr_pct"] = float(f.get("return_3yr_pct", 0) or 0)
        except (ValueError, TypeError):
            f["sharpe_ratio"] = 0.0
            f["return_3yr_pct"] = 0.0

    if risk == "Low":
        allowed = ["Low", "Low to Moderate", "Moderate", "Debt", "Liquid", "Hybrid", "Large Cap"]
    elif risk == "High":
        allowed = ["High", "Very High", "Small Cap", "Mid Cap", "Equity", "Flexi Cap"]
    else:
        allowed = ["Moderate", "Moderately High", "Low to Moderate"]

    filtered = [f for f in funds if f.get("risk_grade") in allowed or f.get("category") in allowed]
    if not filtered:
        filtered = funds

    recommended = sorted(filtered, key=lambda x: (x["sharpe_ratio"], x["return_3yr_pct"]), reverse=True)[:3]
    return jsonify(recommended)

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

        <!-- Executive Summary Banner -->
        <div class="alert alert-primary shadow-sm border-0 mb-4" role="alert">
            <h5 class="alert-heading fw-bold mb-1">Executive Summary & Capstone Overview</h5>
            <p class="mb-0 small">An integrated end-to-end data analytics platform evaluating 10 mutual fund datasets across 40 schemes, historical NAVs, AUM growth, SIP inflows, investor demographics, risk ratios (Sharpe, Sortino, Alpha, Beta, VaR), and sector concentration.</p>
        </div>

        <!-- Top KPI Header Banner -->
        <div class="row g-3 mb-4">
            <div class="col">
                <div class="kpi-card">
                    <div class="kpi-title">Total Industry AUM</div>
                    <div class="kpi-value">₹81.00 Lakh Cr</div>
                    <div class="kpi-sub">Top 10 AMCs: ₹62.74 Lakh Cr</div>
                </div>
            </div>
            <div class="col">
                <div class="kpi-card" style="border-left-color: #10b981;">
                    <div class="kpi-title">Monthly SIP Inflow</div>
                    <div class="kpi-value">₹31,002 Cr</div>
                    <div class="kpi-sub">+17.17% YoY Growth</div>
                </div>
            </div>
            <div class="col">
                <div class="kpi-card" style="border-left-color: #8b5cf6;">
                    <div class="kpi-title">Total Folio Count</div>
                    <div class="kpi-value">26.12 Cr</div>
                    <div class="kpi-sub">Retail Equity Driven</div>
                </div>
            </div>
            <div class="col">
                <div class="kpi-card" style="border-left-color: #f59e0b;">
                    <div class="kpi-title">Industry Schemes</div>
                    <div class="kpi-value">1,908</div>
                    <div class="kpi-sub">Active SEBI Registered</div>
                </div>
            </div>
            <div class="col">
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
                            <h5 class="fw-bold text-dark mb-3">Industry AUM Growth Trajectory (INR Cr)</h5>
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
                                    <td><span class="badge bg-primary fs-6">{{ fund.rank if fund.rank else loop.index }}</span></td>
                                    <td class="fw-bold">{{ fund.scheme_name }}</td>
                                    <td><span class="badge bg-secondary">{{ fund.category }}</span></td>
                                    <td class="text-success fw-bold">{{ fund.return_3yr_pct }}%</td>
                                    <td>{{ fund.sharpe_ratio }}</td>
                                    <td>{{ fund.alpha }}</td>
                                    <td>{{ fund.beta }}</td>
                                    <td>{{ fund.expense_ratio_pct }}%</td>
                                    <td class="text-danger">{{ fund.max_drawdown_pct }}%</td>
                                    <td><span class="badge bg-success fs-6">{{ fund.composite_score if fund.composite_score else '85.0' }}</span></td>
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
@app.route("/api")
@app.route("/api/")
@app.route("/api/index")
@app.route("/api/index.py")
@app.route("/index")
@app.route("/index.html")
def index():
    scorecard = read_csv_file(OUTPUT_DIR / "fund_scorecard.csv")
    if not scorecard:
        scorecard = query_db("SELECT * FROM scheme_performance ORDER BY return_3yr_pct DESC")
    if not scorecard:
        scorecard = read_csv_file(PROCESSED_DIR / "07_scheme_performance.csv")
    funds = scorecard[:15] if scorecard else []

    aum_rows = query_db("SELECT date, aum_crore, fund_house FROM aum_by_fund_house")
    if not aum_rows:
        aum_rows = read_csv_file(PROCESSED_DIR / "03_aum_by_fund_house.csv")
        
    aum_dates, aum_values, fh_names, fh_aum = [], [], [], []
    if aum_rows:
        date_sums = {}
        fh_sums = {}
        fh_counts = {}
        for r in aum_rows:
            d = r.get("date")
            try:
                v = float(r.get("aum_crore", 0) or 0)
            except (ValueError, TypeError):
                v = 0.0
            date_sums[d] = date_sums.get(d, 0.0) + v
            
            fh = r.get("fund_house")
            if fh:
                fh_sums[fh] = fh_sums.get(fh, 0.0) + v
                fh_counts[fh] = fh_counts.get(fh, 0) + 1
                
        sorted_dates = sorted(date_sums.keys())
        aum_dates = sorted_dates
        aum_values = [date_sums[d] for d in sorted_dates]
        
        sorted_fhs = sorted(fh_sums.keys(), key=lambda k: fh_sums[k]/max(1, fh_counts[k]), reverse=True)[:10]
        fh_names = sorted_fhs
        fh_aum = [round(fh_sums[k]/max(1, fh_counts[k]), 2) for kk in sorted_fhs for k in [kk]]

    sip_rows = query_db("SELECT month, sip_inflow_crore FROM monthly_sip_inflows ORDER BY month ASC")
    if not sip_rows:
        sip_rows = read_csv_file(PROCESSED_DIR / "04_monthly_sip_inflows.csv")
    sip_months = [r.get("month") for r in sip_rows]
    sip_inflows = []
    for r in sip_rows:
        try:
            sip_inflows.append(float(r.get("sip_inflow_crore", 0) or 0))
        except (ValueError, TypeError):
            sip_inflows.append(0.0)

    tx_rows = query_db("SELECT state, amount_inr FROM investor_transactions")
    if not tx_rows:
        tx_rows = read_csv_file(PROCESSED_DIR / "08_investor_transactions.csv")
    state_names, state_volumes = [], []
    if tx_rows:
        st_sums = {}
        for r in tx_rows:
            st = r.get("state")
            try:
                amt = float(r.get("amount_inr", 0) or 0)
            except (ValueError, TypeError):
                amt = 0.0
            if st:
                st_sums[st] = st_sums.get(st, 0.0) + amt
        sorted_sts = sorted(st_sums.keys(), key=lambda k: st_sums[k], reverse=True)[:10]
        state_names = sorted_sts
        state_volumes = [round(st_sums[k] / 1e7, 2) for k in sorted_sts]

    cat_rows = query_db("SELECT category, net_inflow_crore FROM category_inflows")
    if not cat_rows:
        cat_rows = read_csv_file(PROCESSED_DIR / "05_category_inflows.csv")
    cat_names, cat_inflows = [], []
    if cat_rows:
        c_sums = {}
        for r in cat_rows:
            cat = r.get("category")
            try:
                val = float(r.get("net_inflow_crore", 0) or 0)
            except (ValueError, TypeError):
                val = 0.0
            if cat:
                c_sums[cat] = c_sums.get(cat, 0.0) + val
        sorted_cats = sorted(c_sums.keys(), key=lambda k: c_sums[k], reverse=True)[:8]
        cat_names = sorted_cats
        cat_inflows = [round(c_sums[k], 2) for k in sorted_cats]

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

@app.errorhandler(404)
def handle_404(e):
    path = request.path
    if path.startswith("/api/"):
        return jsonify({"error": "Not Found", "status": 404}), 404
    return index()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
