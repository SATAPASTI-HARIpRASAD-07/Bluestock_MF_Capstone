"""
PDF Report Generation Module — ReportLab 2-Page Tear Sheets.
"""

import os
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from src.analytics.health_score import FinancialHealthScoreEngine
from src.intelligence.pros_cons import ProsAndConsGenerator

class PDFReportGenerator:
    def __init__(self, db_path: str = "db/nifty100.db", output_dir: str = "reports/company"):
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.health_engine = FinancialHealthScoreEngine(self.db_path)
        self.pros_cons_engine = ProsAndConsGenerator(self.db_path)

    def generate_company_tearsheet(self, company_id: str) -> str:
        """
        Generate 2-page PDF Tear Sheet for a specific company.
        """
        conn = sqlite3.connect(self.db_path)
        comp_df = pd.read_sql_query("SELECT * FROM companies WHERE company_id = ?", conn, params=(company_id,))
        rat_df = pd.read_sql_query("SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year DESC LIMIT 5", conn, params=(company_id,))
        conn.close()

        if comp_df.empty:
            return ""

        comp_info = comp_df.iloc[0]
        pdf_path = os.path.join(self.output_dir, f"{company_id}_tearsheet.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0F172A'), spaceAfter=6)
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#475569'), spaceAfter=12)
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1E3A8A'), spaceBefore=10, spaceAfter=8)
        body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=9, leading=12)

        story = []

        # PAGE 1: Company Profile & Key Financial Trends
        story.append(Paragraph(f"<b>BLUESTOCK FINTECH</b> — Financial Intelligence Tear Sheet", ParagraphStyle('Header', fontSize=9, textColor=colors.HexColor('#2563EB'))))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>{comp_info['company_name']}</b> ({company_id})", title_style))
        story.append(Paragraph(f"Sector: {comp_info['broad_sector']} | Industry: {comp_info['sub_sector']} | Market Cap: {comp_info['market_cap_category']} (Weight: {comp_info['index_weight_pct']}%)", subtitle_style))
        story.append(Spacer(1, 10))

        # Financial Health Score Card
        health_data = self.health_engine.compute_score_for_company(company_id)
        score_table_data = [
            ["Financial Health Score", "Risk / Health Band", "Profitability (30%)", "Solvency (25%)", "Cash Flow (25%)"],
            [f"{health_data['score']:.1f} / 100", health_data['band'], 
             f"{health_data['breakdown']['Profitability (30%)']:.1f}",
             f"{health_data['breakdown']['Solvency (25%)']:.1f}",
             f"{health_data['breakdown']['Cash Flow Quality (25%)']:.1f}"]
        ]
        score_table = Table(score_table_data, colWidths=[120, 150, 90, 90, 90])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F1F5F9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 15))

        # Financial Performance History Table
        story.append(Paragraph("<b>5-Year Financial Summary & Key Ratios</b>", section_style))
        if not rat_df.empty:
            headers = ["Metric / Year"] + list(rat_df["year"].values)[::-1]
            rows = [
                ["ROE (%)"] + [f"{x:.1f}%" if pd.notnull(x) else "N/A" for x in rat_df["return_on_equity_pct"].values[::-1]],
                ["OPM (%)"] + [f"{x:.1f}%" if pd.notnull(x) else "N/A" for x in rat_df["operating_profit_margin_pct"].values[::-1]],
                ["Debt to Equity"] + [f"{x:.2f}" if pd.notnull(x) else "0.00" for x in rat_df["debt_to_equity"].values[::-1]],
                ["CFO (Rs Cr)"] + [f"{x:,.0f}" if pd.notnull(x) else "0" for x in rat_df["cash_from_operations_cr"].values[::-1]],
                ["CapEx (Rs Cr)"] + [f"{x:,.0f}" if pd.notnull(x) else "0" for x in rat_df["capex_cr"].values[::-1]],
                ["Free Cash Flow (Rs Cr)"] + [f"{x:,.0f}" if pd.notnull(x) else "0" for x in rat_df["free_cash_flow_cr"].values[::-1]],
                ["EPS (Rs)"] + [f"{x:.1f}" if pd.notnull(x) else "0.0" for x in rat_df["earnings_per_share"].values[::-1]],
            ]
            hist_table = Table([headers] + rows, colWidths=[140] + [75]*(len(headers)-1))
            hist_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(hist_table)

        # PAGE BREAK
        story.append(PageBreak())

        # PAGE 2: Qualitative Insights, Observations & Disclaimers
        story.append(Paragraph("<b>QUALITATIVE INTELLIGENCE & OBSERVED RISKS</b>", section_style))
        obs = self.pros_cons_engine.generate_observations(company_id)

        story.append(Paragraph("<b>Positive Investment Drivers (Pros)</b>", ParagraphStyle('SubHeader', fontSize=11, textColor=colors.HexColor('#166534'), spaceBefore=6)))
        for p in obs["pros"]:
            story.append(Paragraph(f"• {p['text']}", body_style))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 8))
        story.append(Paragraph("<b>Risk Factors & Vulnerabilities (Cons)</b>", ParagraphStyle('SubHeader2', fontSize=11, textColor=colors.HexColor('#991B1B'), spaceBefore=6)))
        for c in obs["cons"]:
            story.append(Paragraph(f"• {c['text']}", body_style))
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>DISCLAIMER & METHODOLOGY</b>", ParagraphStyle('DiscTitle', fontSize=10, textColor=colors.HexColor('#475569'))))
        story.append(Paragraph("This report was generated by the Bluestock Nifty 100 Financial Intelligence Platform as part of an automated analytical workflow. All data is derived from official financial disclosures. Simulated stock price data and computed metrics are provided for analytical purposes only and do not constitute investment advice.", ParagraphStyle('Disc', fontSize=7, textColor=colors.HexColor('#64748B'), leading=10)))

        doc.build(story)
        return pdf_path
