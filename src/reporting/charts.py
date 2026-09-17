"""
Visualization & Chart Engine — Plotly & Matplotlib Routines.
"""

import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any

def create_peer_radar_chart(company_name: str, comp_metrics: Dict[str, float], peer_avg_metrics: Dict[str, float]) -> go.Figure:
    """
    Generate interactive Plotly Radar Chart comparing company against peer group average.
    """
    categories = list(comp_metrics.keys())
    comp_vals = [comp_metrics[c] for c in categories]
    peer_vals = [peer_avg_metrics[c] for c in categories]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=comp_vals,
        theta=categories,
        fill='toself',
        name=company_name,
        line_color='#2563EB'
    ))
    fig.add_trace(go.Scatterpolar(
        r=peer_vals,
        theta=categories,
        fill='toself',
        name='Peer Group Average',
        line_color='#94A3B8'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title=f"Peer Comparison Benchmark — {company_name}",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

def create_capital_allocation_treemap(df: pd.DataFrame) -> go.Figure:
    """
    Generate interactive Plotly Treemap grouping 92 companies by capital allocation pattern.
    """
    fig = px.treemap(
        df,
        path=['broad_sector', 'pattern_description', 'company_id'],
        values='market_cap_crore',
        color='cfo_pat_ratio',
        color_continuous_scale='Viridis',
        title="Nifty 100 Capital Allocation Matrix & Cash Flow Patterns"
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig

def save_correlation_heatmap(corr_df: pd.DataFrame, output_path: str = "outputs/correlation_heatmap.png"):
    """
    Generate and save correlation heatmap png image.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_df, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Nifty 100 Portfolio Metric Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
