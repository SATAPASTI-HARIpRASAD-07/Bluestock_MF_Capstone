import json
import logging
from pathlib import Path
import zipfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = BASE_DIR / "dashboard"
DATA_DIR = DASHBOARD_DIR / "data"
PBIX_PATH = DASHBOARD_DIR / "bluestock_mf.pbix"

def build_datamodel_schema():
    """Build Power BI DataModelSchema JSON."""
    tables = [
        {
            "name": "dim_fund",
            "columns": [
                {"name": "amfi_code", "dataType": "int64"},
                {"name": "fund_house", "dataType": "string"},
                {"name": "scheme_name", "dataType": "string"},
                {"name": "category", "dataType": "string"},
                {"name": "sub_category", "dataType": "string"},
                {"name": "plan", "dataType": "string"},
                {"name": "launch_date", "dataType": "dateTime"},
                {"name": "benchmark", "dataType": "string"},
                {"name": "expense_ratio_pct", "dataType": "double"},
                {"name": "exit_load_pct", "dataType": "double"},
                {"name": "min_sip_amount", "dataType": "int64"},
                {"name": "min_lumpsum_amount", "dataType": "int64"},
                {"name": "fund_manager", "dataType": "string"},
                {"name": "risk_category", "dataType": "string"},
                {"name": "sebi_category_code", "dataType": "string"}
            ],
            "partitions": [{
                "name": "dim_fund",
                "source": {
                    "type": "m",
                    "expression": f'let Source = Csv.Document(File.Contents("{DATA_DIR.as_posix()}/dim_fund.csv"),[Delimiter=",", Columns=15, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                }
            }]
        },
        {
            "name": "dim_date",
            "columns": [
                {"name": "date_key", "dataType": "int64"},
                {"name": "full_date", "dataType": "dateTime"},
                {"name": "year", "dataType": "int64"},
                {"name": "quarter", "dataType": "int64"},
                {"name": "month", "dataType": "int64"},
                {"name": "month_name", "dataType": "string"},
                {"name": "day", "dataType": "int64"},
                {"name": "day_of_week", "dataType": "int64"}
            ],
            "partitions": [{
                "name": "dim_date",
                "source": {
                    "type": "m",
                    "expression": f'let Source = Csv.Document(File.Contents("{DATA_DIR.as_posix()}/dim_date.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                }
            }]
        },
        {
            "name": "fact_nav",
            "columns": [
                {"name": "amfi_code", "dataType": "int64"},
                {"name": "date", "dataType": "dateTime"},
                {"name": "nav", "dataType": "double"}
            ],
            "partitions": [{
                "name": "fact_nav",
                "source": {
                    "type": "m",
                    "expression": f'let Source = Csv.Document(File.Contents("{DATA_DIR.as_posix()}/fact_nav.csv"),[Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                }
            }]
        },
        {
            "name": "fact_transactions",
            "columns": [
                {"name": "investor_id", "dataType": "string"},
                {"name": "transaction_date", "dataType": "dateTime"},
                {"name": "amfi_code", "dataType": "int64"},
                {"name": "transaction_type", "dataType": "string"},
                {"name": "amount_inr", "dataType": "double"},
                {"name": "state", "dataType": "string"},
                {"name": "city", "dataType": "string"},
                {"name": "city_tier", "dataType": "string"},
                {"name": "age_group", "dataType": "string"},
                {"name": "gender", "dataType": "string"},
                {"name": "annual_income_lakh", "dataType": "double"},
                {"name": "payment_mode", "dataType": "string"},
                {"name": "kyc_status", "dataType": "string"}
            ],
            "partitions": [{
                "name": "fact_transactions",
                "source": {
                    "type": "m",
                    "expression": f'let Source = Csv.Document(File.Contents("{DATA_DIR.as_posix()}/fact_transactions.csv"),[Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                }
            }]
        },
        {
            "name": "fact_performance",
            "columns": [
                {"name": "amfi_code", "dataType": "int64"},
                {"name": "scheme_name", "dataType": "string"},
                {"name": "fund_house", "dataType": "string"},
                {"name": "category", "dataType": "string"},
                {"name": "plan", "dataType": "string"},
                {"name": "return_1yr_pct", "dataType": "double"},
                {"name": "return_3yr_pct", "dataType": "double"},
                {"name": "return_5yr_pct", "dataType": "double"},
                {"name": "benchmark_3yr_pct", "dataType": "double"},
                {"name": "alpha", "dataType": "double"},
                {"name": "beta", "dataType": "double"},
                {"name": "sharpe_ratio", "dataType": "double"},
                {"name": "sortino_ratio", "dataType": "double"},
                {"name": "std_dev_ann_pct", "dataType": "double"},
                {"name": "max_drawdown_pct", "dataType": "double"},
                {"name": "aum_crore", "dataType": "double"},
                {"name": "expense_ratio_pct", "dataType": "double"},
                {"name": "morningstar_rating", "dataType": "int64"},
                {"name": "anomaly_flag", "dataType": "int64"}
            ],
            "partitions": [{
                "name": "fact_performance",
                "source": {
                    "type": "m",
                    "expression": f'let Source = Csv.Document(File.Contents("{DATA_DIR.as_posix()}/fact_performance.csv"),[Delimiter=",", Columns=19, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                }
            }]
        },
        {
            "name": "fact_aum",
            "columns": [
                {"name": "date", "dataType": "dateTime"},
                {"name": "fund_house", "dataType": "string"},
                {"name": "aum_lakh_crore", "dataType": "double"},
                {"name": "aum_crore", "dataType": "double"},
                {"name": "num_schemes", "dataType": "int64"}
            ],
            "partitions": [{
                "name": "fact_aum",
                "source": {
                    "type": "m",
                    "expression": f'let Source = Csv.Document(File.Contents("{DATA_DIR.as_posix()}/fact_aum.csv"),[Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                }
            }]
        },
        {
            "name": "fact_sip_industry",
            "columns": [
                {"name": "month", "dataType": "dateTime"},
                {"name": "sip_inflow_crore", "dataType": "double"},
                {"name": "active_sip_accounts_crore", "dataType": "double"},
                {"name": "new_sip_accounts_lakh", "dataType": "double"},
                {"name": "sip_aum_lakh_crore", "dataType": "double"},
                {"name": "yoy_growth_pct", "dataType": "double"}
            ],
            "partitions": [{
                "name": "fact_sip_industry",
                "source": {
                    "type": "m",
                    "expression": f'let Source = Csv.Document(File.Contents("{DATA_DIR.as_posix()}/fact_sip_industry.csv"),[Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                }
            }]
        },
        {
            "name": "fact_industry_folio",
            "columns": [
                {"name": "month", "dataType": "dateTime"},
                {"name": "total_folios_crore", "dataType": "double"},
                {"name": "equity_folios_crore", "dataType": "double"},
                {"name": "debt_folios_crore", "dataType": "double"},
                {"name": "hybrid_folios_crore", "dataType": "double"},
                {"name": "others_folios_crore", "dataType": "double"}
            ],
            "partitions": [{
                "name": "fact_industry_folio",
                "source": {
                    "type": "m",
                    "expression": f'let Source = Csv.Document(File.Contents("{DATA_DIR.as_posix()}/fact_industry_folio.csv"),[Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                }
            }]
        },
        {
            "name": "fact_benchmark",
            "columns": [
                {"name": "date", "dataType": "dateTime"},
                {"name": "index_name", "dataType": "string"},
                {"name": "close_value", "dataType": "double"}
            ],
            "partitions": [{
                "name": "fact_benchmark",
                "source": {
                    "type": "m",
                    "expression": f'let Source = Csv.Document(File.Contents("{DATA_DIR.as_posix()}/fact_benchmark.csv"),[Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]), #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]) in #"Promoted Headers"'
                }
            }]
        },
        {
            "name": "_Measures",
            "columns": [{"name": "MeasurePlaceholder", "dataType": "string"}],
            "measures": [
                {"name": "Total Industry AUM Cr", "expression": 'VAR LatestDate = MAX(fact_aum[date]) RETURN CALCULATE(SUM(fact_aum[aum_crore]), fact_aum[date] = LatestDate)'},
                {"name": "Latest Monthly SIP Inflow Cr", "expression": 'VAR LatestMonth = MAX(fact_sip_industry[month]) RETURN CALCULATE(SUM(fact_sip_industry[sip_inflow_crore]), fact_sip_industry[month] = LatestMonth)'},
                {"name": "Total Folio Count Cr", "expression": 'VAR LatestMonth = MAX(fact_industry_folio[month]) RETURN CALCULATE(SUM(fact_industry_folio[total_folios_crore]), fact_industry_folio[month] = LatestMonth)'},
                {"name": "Active Schemes Count", "expression": "DISTINCTCOUNT(dim_fund[amfi_code])"},
                {"name": "Avg 3Yr CAGR Return %", "expression": "AVERAGE(fact_performance[return_3yr_pct])"},
                {"name": "Avg Sharpe Ratio", "expression": "AVERAGE(fact_performance[sharpe_ratio])"},
                {"name": "Avg Alpha", "expression": "AVERAGE(fact_performance[alpha])"},
                {"name": "Avg Beta", "expression": "AVERAGE(fact_performance[beta])"},
                {"name": "Total Investor Transactions", "expression": "COUNTROWS(fact_transactions)"},
                {"name": "Total Investment Volume Cr", "expression": "DIVIDE(SUM(fact_transactions[amount_inr]), 10000000)"},
                {"name": "SIP Volume Cr", "expression": 'CALCULATE([Total Investment Volume Cr], fact_transactions[transaction_type] = "SIP")'},
                {"name": "Lumpsum Volume Cr", "expression": 'CALCULATE([Total Investment Volume Cr], fact_transactions[transaction_type] = "Lumpsum")'},
                {"name": "Redemption Volume Cr", "expression": 'CALCULATE([Total Investment Volume Cr], fact_transactions[transaction_type] = "Redemption")'}
            ],
            "partitions": [{
                "name": "_Measures",
                "source": {"type": "m", "expression": "#table({\"MeasurePlaceholder\"}, {})"}
            }]
        }
    ]

    relationships = [
        {"name": "rel_fund_nav", "fromTable": "fact_nav", "fromColumn": "amfi_code", "toTable": "dim_fund", "toColumn": "amfi_code"},
        {"name": "rel_fund_tx", "fromTable": "fact_transactions", "fromColumn": "amfi_code", "toTable": "dim_fund", "toColumn": "amfi_code"},
        {"name": "rel_fund_perf", "fromTable": "fact_performance", "fromColumn": "amfi_code", "toTable": "dim_fund", "toColumn": "amfi_code"},
        {"name": "rel_date_nav", "fromTable": "fact_nav", "fromColumn": "date", "toTable": "dim_date", "toColumn": "full_date"},
        {"name": "rel_date_tx", "fromTable": "fact_transactions", "fromColumn": "transaction_date", "toTable": "dim_date", "toColumn": "full_date"}
    ]

    model_schema = {
        "name": "bluestock_mf",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-US",
            "tables": tables,
            "relationships": relationships
        }
    }
    return json.dumps(model_schema, indent=2)

def build_report_layout():
    """Build Power BI Report Layout JSON defining 4 pages & visual containers."""
    pages = [
        {
            "id": 0,
            "name": "ReportSection1",
            "displayName": "Industry Overview",
            "width": 1280,
            "height": 720,
            "visualContainers": [
                {
                    "x": 20, "y": 20, "width": 230, "height": 100,
                    "config": json.dumps({"name": "card_aum", "singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "Total Industry AUM"}]}}})
                },
                {
                    "x": 270, "y": 20, "width": 230, "height": 100,
                    "config": json.dumps({"name": "card_sip", "singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "Monthly SIP Inflow"}]}}})
                },
                {
                    "x": 520, "y": 20, "width": 230, "height": 100,
                    "config": json.dumps({"name": "card_folio", "singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "Total Folio Count"}]}}})
                },
                {
                    "x": 770, "y": 20, "width": 230, "height": 100,
                    "config": json.dumps({"name": "card_ind_schemes", "singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "Industry Schemes"}]}}})
                },
                {
                    "x": 1020, "y": 20, "width": 230, "height": 100,
                    "config": json.dumps({"name": "card_analyzed_schemes", "singleVisual": {"visualType": "card", "projections": {"Values": [{"queryRef": "Schemes Analyzed"}]}}})
                },
                {
                    "x": 20, "y": 140, "width": 610, "height": 540,
                    "config": json.dumps({"name": "line_aum_trend", "singleVisual": {"visualType": "lineChart", "projections": {"Category": [{"queryRef": "fact_aum.date"}], "Y": [{"queryRef": "fact_aum.aum_crore"}]}}})
                },
                {
                    "x": 650, "y": 140, "width": 600, "height": 540,
                    "config": json.dumps({"name": "bar_top_amc", "singleVisual": {"visualType": "barChart", "projections": {"Category": [{"queryRef": "fact_aum.fund_house"}], "Y": [{"queryRef": "fact_aum.aum_crore"}]}}})
                }
            ]
        },
        {
            "id": 1,
            "name": "ReportSection2",
            "displayName": "Fund Performance & Scorecard",
            "width": 1280,
            "height": 720,
            "visualContainers": [
                {
                    "x": 20, "y": 20, "width": 280, "height": 660,
                    "config": json.dumps({"name": "slicers_panel", "singleVisual": {"visualType": "slicer", "projections": {"Values": [{"queryRef": "dim_fund.category"}]}}})
                },
                {
                    "x": 320, "y": 20, "width": 460, "height": 320,
                    "config": json.dumps({"name": "scatter_risk_return", "singleVisual": {"visualType": "scatterChart", "projections": {"X": [{"queryRef": "fact_performance.std_dev_ann_pct"}], "Y": [{"queryRef": "fact_performance.return_3yr_pct"}]}}})
                },
                {
                    "x": 800, "y": 20, "width": 460, "height": 320,
                    "config": json.dumps({"name": "column_bm_comp", "singleVisual": {"visualType": "columnChart", "projections": {"Category": [{"queryRef": "fact_performance.scheme_name"}], "Y": [{"queryRef": "fact_performance.return_3yr_pct"}]}}})
                },
                {
                    "x": 320, "y": 360, "width": 940, "height": 320,
                    "config": json.dumps({"name": "grid_scorecard", "singleVisual": {"visualType": "table", "projections": {"Values": [{"queryRef": "fact_performance.scheme_name"}, {"queryRef": "fact_performance.return_3yr_pct"}, {"queryRef": "fact_performance.sharpe_ratio"}]}}})
                }
            ]
        },
        {
            "id": 2,
            "name": "ReportSection3",
            "displayName": "Investor Analytics",
            "width": 1280,
            "height": 720,
            "visualContainers": [
                {
                    "x": 20, "y": 20, "width": 600, "height": 320,
                    "config": json.dumps({"name": "bar_state_vol", "singleVisual": {"visualType": "barChart", "projections": {"Category": [{"queryRef": "fact_transactions.state"}], "Y": [{"queryRef": "fact_transactions.amount_inr"}]}}})
                },
                {
                    "x": 640, "y": 20, "width": 610, "height": 320,
                    "config": json.dumps({"name": "donut_type_split", "singleVisual": {"visualType": "pieChart", "projections": {"Category": [{"queryRef": "fact_transactions.transaction_type"}], "Y": [{"queryRef": "fact_transactions.amount_inr"}]}}})
                },
                {
                    "x": 20, "y": 360, "width": 1230, "height": 320,
                    "config": json.dumps({"name": "column_age_vol", "singleVisual": {"visualType": "columnChart", "projections": {"Category": [{"queryRef": "fact_transactions.age_group"}], "Y": [{"queryRef": "fact_transactions.amount_inr"}]}}})
                }
            ]
        },
        {
            "id": 3,
            "name": "ReportSection4",
            "displayName": "SIP & Market Trends",
            "width": 1280,
            "height": 720,
            "visualContainers": [
                {
                    "x": 20, "y": 20, "width": 600, "height": 320,
                    "config": json.dumps({"name": "line_sip_trend", "singleVisual": {"visualType": "lineChart", "projections": {"Category": [{"queryRef": "fact_sip_industry.month"}], "Y": [{"queryRef": "fact_sip_industry.sip_inflow_crore"}]}}})
                },
                {
                    "x": 640, "y": 20, "width": 610, "height": 320,
                    "config": json.dumps({"name": "line_nifty_trend", "singleVisual": {"visualType": "lineChart", "projections": {"Category": [{"queryRef": "fact_benchmark.date"}], "Y": [{"queryRef": "fact_benchmark.close_value"}]}}})
                },
                {
                    "x": 20, "y": 360, "width": 1230, "height": 320,
                    "config": json.dumps({"name": "bar_cat_inflow", "singleVisual": {"visualType": "barChart", "projections": {"Category": [{"queryRef": "fact_category_inflows.category"}], "Y": [{"queryRef": "fact_category_inflows.net_inflow_crore"}]}}})
                }
            ]
        }
    ]

    layout_dict = {
        "version": "1.25",
        "theme": "Standard",
        "sections": pages
    }
    return json.dumps(layout_dict, indent=2)

def build_pbix_package():
    logger.info(f"Building valid Power BI Desktop PBIX file at {PBIX_PATH}...")
    
    content_types_xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="xml" ContentType="application/xml" />\n'
        '  <Default Extension="json" ContentType="application/json" />\n'
        '  <Override PartName="/Version" ContentType="text/plain" />\n'
        '  <Override PartName="/DataModelSchema" ContentType="application/json" />\n'
        '  <Override PartName="/Report/Layout" ContentType="application/json" />\n'
        '  <Override PartName="/Settings" ContentType="application/json" />\n'
        '</Types>'
    )
    
    version_text = "1.25"
    settings_json = json.dumps({"useNewFilterPane": True, "allowChangeFilterTypes": True}, indent=2)
    diagram_layout_json = json.dumps({"version": "1.0", "diagrams": []}, indent=2)
    
    datamodel_schema = build_datamodel_schema()
    report_layout = build_report_layout()
    
    with zipfile.ZipFile(PBIX_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("Version", version_text)
        zf.writestr("Settings", settings_json)
        zf.writestr("DiagramLayout", diagram_layout_json)
        zf.writestr("DataModelSchema", datamodel_schema)
        zf.writestr("Report/Layout", report_layout)
        
    size_bytes = PBIX_PATH.stat().st_size
    logger.info(f"Successfully generated Power BI Desktop file {PBIX_PATH} ({size_bytes:,} bytes)")
    return size_bytes

if __name__ == "__main__":
    build_pbix_package()
