"""
Visualization Suite.
Generates executive-quality Plotly figures with consistent styling,
informative tooltips, and explicit axis labeling.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any

# Standard Executive Color Palette
PRIMARY_COLOR = "#1E3A8A"     # Navy Blue
SECONDARY_COLOR = "#0D9488"   # Teal
ACCENT_COLOR = "#F59E0B"      # Amber
DANGER_COLOR = "#DC2626"      # Coral Red
SUCCESS_COLOR = "#10B981"     # Emerald
BG_COLOR = "#FFFFFF"

def format_fig(fig: go.Figure, title: str) -> go.Figure:
    """Applies corporate executive styling to Plotly charts."""
    fig.update_layout(
        title={
            'text': f"<b>{title}</b>",
            'y': 0.95,
            'x': 0.05,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': {'size': 18, 'family': 'Arial, sans-serif'}
        },
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(color="#1F2937"),
        hoverlabel=dict(bgcolor="white", font_size=13)
    )
    return fig

def plot_monthly_revenue_trend(monthly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_df['year_month'],
        y=monthly_df['net_revenue'],
        name='Net Revenue',
        marker_color=PRIMARY_COLOR,
        hovertemplate="<b>%{x}</b><br>Net Revenue: $%{y:,.2f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=monthly_df['year_month'],
        y=monthly_df['rolling_3m_revenue'],
        mode='lines+markers',
        name='3-Month Moving Avg',
        line=dict(color=ACCENT_COLOR, width=3),
        hovertemplate="<b>3M Moving Avg</b>: $%{y:,.2f}<extra></extra>"
    ))
    fig.update_xaxes(title="Year-Month", tickangle=-45)
    fig.update_yaxes(title="Revenue (USD)", tickprefix="$")
    return format_fig(fig, "Monthly Net Revenue Trend & Trajectory")

def plot_regional_revenue_bar(regional_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        regional_df,
        x='region',
        y='net_revenue',
        color='gross_margin_pct',
        color_continuous_scale='Teal',
        labels={'net_revenue': 'Net Revenue ($)', 'region': 'Region', 'gross_margin_pct': 'Margin %'},
        text=regional_df['revenue_share'].apply(lambda x: f"{x*100:.1f}%")
    )
    fig.update_traces(
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Net Revenue: $%{y:,.2f}<br>Share: %{text}<extra></extra>"
    )
    fig.update_yaxes(tickprefix="$")
    return format_fig(fig, "Regional Net Revenue & Profitability Share")

def plot_regional_revenue_donut(regional_df: pd.DataFrame) -> go.Figure:
    fig = px.pie(
        regional_df,
        names='region',
        values='net_revenue',
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_traces(
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )
    return format_fig(fig, "Geographic Revenue Share Distribution")

def plot_pareto_curve(pareto_data: Dict[str, Any], entity_name: str = "Brand") -> go.Figure:
    table = pareto_data['table']
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=table[table.columns[0]],
        y=table['net_revenue'],
        name='Net Revenue ($)',
        marker_color=PRIMARY_COLOR,
        hovertemplate=f"<b>%{{x}}</b><br>Net Revenue: $%{{y:,.2f}}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=table[table.columns[0]],
        y=table['cumulative_share'] * 100,
        name='Cumulative Contribution %',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color=DANGER_COLOR, width=2.5),
        hovertemplate=f"<b>%{{x}}</b><br>Cumulative: %{{y:.1f}}%<extra></extra>"
    ))
    # 80% Pareto threshold line
    fig.add_hline(y=80, line_dash="dash", line_color="#4B5563", yref='y2',
                  annotation_text="80% Pareto Benchmark", annotation_position="top left")
    
    fig.update_layout(
        yaxis=dict(title="Net Revenue (USD)", tickprefix="$"),
        yaxis2=dict(title="Cumulative Share (%)", overlaying='y', side='right', range=[0, 105], ticksuffix="%"),
        xaxis=dict(title=entity_name, tickangle=-45),
        legend=dict(x=0.01, y=0.99)
    )
    return format_fig(fig, f"Pareto 80/20 Concentration Analysis — {entity_name}")

def plot_category_revenue_margin(cat_df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        cat_df,
        x='net_revenue',
        y='gross_margin_pct',
        size='units',
        color='classification',
        text='category',
        labels={'net_revenue': 'Net Revenue ($)', 'gross_margin_pct': 'Gross Margin %', 'units': 'Volume Units'},
        color_discrete_map={
            'Margin & Revenue Leader': SUCCESS_COLOR,
            'Volume Driver (High Vol / Lower Margin)': PRIMARY_COLOR,
            'Margin Specialist (Niche High Profit)': SECONDARY_COLOR,
            'Discount-Dependent': ACCENT_COLOR,
            'Underperformer': DANGER_COLOR
        }
    )
    fig.update_traces(
        textposition='top center',
        hovertemplate="<b>%{text}</b><br>Revenue: $%{x:,.2f}<br>Margin: %{y:.1%}<extra></extra>"
    )
    fig.update_xaxes(tickprefix="$")
    fig.update_yaxes(tickformat=".1%")
    return format_fig(fig, "Category Economics: Revenue vs Margin Matrix")

def plot_brand_risk_matrix(brand_df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        brand_df,
        x='revenue_share',
        y='gross_margin_pct',
        size='units',
        color='portfolio_classification',
        text='brand',
        labels={'revenue_share': 'Revenue Share', 'gross_margin_pct': 'Gross Margin %'},
        color_discrete_map={
            'Anchor Brand': PRIMARY_COLOR,
            'Growth Brand': SUCCESS_COLOR,
            'Margin Brand': SECONDARY_COLOR,
            'Risk Brand': DANGER_COLOR,
            'Core Portfolio': '#6B7280'
        }
    )
    fig.update_traces(
        textposition='top center',
        hovertemplate="<b>%{text}</b><br>Share: %{x:.2%}<br>Margin: %{y:.1%}<extra></extra>"
    )
    fig.update_xaxes(tickformat=".1%")
    fig.update_yaxes(tickformat=".1%")
    return format_fig(fig, "Brand Portfolio: Revenue Share vs Gross Margin")

def plot_regional_opportunity_matrix(reg_df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        reg_df,
        x='net_revenue',
        y='growth_rate',
        size='orders',
        color='opportunity_classification',
        text='region',
        labels={'net_revenue': 'Net Revenue ($)', 'growth_rate': 'YoY Revenue Growth Rate', 'orders': 'Order Count'}
    )
    fig.update_traces(
        textposition='top center',
        hovertemplate="<b>%{text}</b><br>Revenue: $%{x:,.2f}<br>Growth: %{y:.1%}<extra></extra>"
    )
    fig.update_xaxes(tickprefix="$")
    fig.update_yaxes(tickformat=".1%")
    return format_fig(fig, "Regional Opportunity Matrix (Revenue x Growth)")

def plot_transit_vs_repeat(transit_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        transit_df,
        x='transit_group',
        y='repeat_rate',
        color='avg_total_orders',
        labels={'transit_group': 'First-Order Transit Time', 'repeat_rate': 'Repeat Purchase Rate', 'avg_total_orders': 'Avg Lifetime Orders'},
        text=transit_df['repeat_rate'].apply(lambda x: f"{x*100:.1f}%")
    )
    fig.update_traces(textposition='outside')
    fig.update_yaxes(tickformat=".1%", title="Repeat Purchase Rate (%)")
    return format_fig(fig, "Transit Performance vs Customer Retention Rate")

def plot_rfm_segments(rfm_summary: list) -> go.Figure:
    df_rfm = pd.DataFrame(rfm_summary)
    fig = px.bar(
        df_rfm,
        x='segment',
        y='total_revenue',
        color='customer_count',
        text=df_rfm['revenue_share'].apply(lambda x: f"{x*100:.1f}%"),
        labels={'total_revenue': 'Total Revenue ($)', 'segment': 'RFM Segment', 'customer_count': 'Customers'}
    )
    fig.update_traces(textposition='outside')
    fig.update_yaxes(tickprefix="$")
    return format_fig(fig, "RFM Customer Segmentation: Revenue Contribution")

def plot_cohort_retention(retention_matrix: pd.DataFrame) -> go.Figure:
    fig = px.imshow(
        retention_matrix * 100,
        labels=dict(x="Months Since First Order", y="Cohort Month", color="Retention %"),
        x=[f"Month {c}" for c in retention_matrix.columns],
        y=[str(idx) for idx in retention_matrix.index],
        color_continuous_scale='Blues',
        text_auto='.1f'
    )
    return format_fig(fig, "Customer Cohort Retention Matrix (%)")
