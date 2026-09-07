"""
Revenue Analytics Engine.
Calculates executive KPIs, temporal trends, MoM/QoQ/YoY growth, and Pareto concentration.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.config import PARETO_THRESHOLDS, TOLERANCE

def compute_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates executive-level commercial KPIs.
    Reconciles order-level net revenue and guarantees programmatic calculation.
    """
    total_gross = float(df['gross_revenue'].sum())
    total_net = float(df['net_revenue'].sum())
    total_cost = float(df['product_cost'].sum())
    total_margin = float(df['margin'].sum())
    total_discount = float(df['discount_amount'].sum())
    
    unique_orders = int(df['order_id'].nunique())
    unique_customers = int(df['customer_id'].nunique())

    # AOV must be calculated as order-level revenue / unique orders
    # We group by order_id to get exact per-order net revenue
    order_revs = df.groupby('order_id')['net_revenue'].sum()
    aov = float(order_revs.mean()) if unique_orders > 0 else 0.0

    gross_margin_pct = (total_margin / total_net) if total_net > 0 else 0.0
    discount_rate = (total_discount / total_gross) if total_gross > 0 else 0.0

    # Repeat Purchase Rate: customers with >= 2 orders / total unique customers
    cust_order_counts = df.groupby('customer_id')['order_id'].nunique()
    repeat_customers = int((cust_order_counts > 1).sum())
    repeat_rate = (repeat_customers / unique_customers) if unique_customers > 0 else 0.0

    # Operational rates
    return_rate = float(df['return_flag'].mean()) if 'return_flag' in df.columns else 0.0
    dispute_rate = float(df['dispute_flag'].mean()) if 'dispute_flag' in df.columns else 0.0
    avg_transit_days = float(df['transit_days'].dropna().mean()) if 'transit_days' in df.columns else None

    # Temporal Growth: YoY (comparing full 2024 to 2023)
    df_temp = df.copy()
    df_temp['order_date'] = pd.to_datetime(df_temp['order_date'])
    yearly_rev = df_temp.groupby(df_temp['order_date'].dt.year)['net_revenue'].sum()
    if 2023 in yearly_rev and 2024 in yearly_rev and yearly_rev[2023] > 0:
        yoy_growth = float((yearly_rev[2024] - yearly_rev[2023]) / yearly_rev[2023])
    else:
        yoy_growth = 0.0

    # Top Region and Top 5 Brand concentration
    reg_rev = df.groupby('region')['net_revenue'].sum()
    top_region_share = float(reg_rev.max() / total_net) if total_net > 0 else 0.0
    top_3_region_share = float(reg_rev.nlargest(3).sum() / total_net) if total_net > 0 else 0.0

    brand_rev = df.groupby('brand')['net_revenue'].sum()
    top_5_brand_share = float(brand_rev.nlargest(5).sum() / total_net) if total_net > 0 else 0.0

    return {
        'total_gross_revenue': round(total_gross, 2),
        'total_net_revenue': round(total_net, 2),
        'total_cost': round(total_cost, 2),
        'margin_contribution': round(total_margin, 2),
        'gross_margin_pct': round(gross_margin_pct, 4),
        'total_orders': unique_orders,
        'total_customers': unique_customers,
        'aov': round(aov, 2),
        'revenue_growth_yoy': round(yoy_growth, 4),
        'discount_rate': round(discount_rate, 4),
        'repeat_purchase_rate': round(repeat_rate, 4),
        'return_rate': round(return_rate, 4),
        'dispute_rate': round(dispute_rate, 4),
        'avg_transit_days': round(avg_transit_days, 2) if avg_transit_days is not None else "Not available in source data.",
        'top_region_share': round(top_region_share, 4),
        'top_3_region_share': round(top_3_region_share, 4),
        'top_5_brand_share': round(top_5_brand_share, 4)
    }

def compute_temporal_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Computes monthly aggregation, MoM growth, and rolling metrics."""
    df_temp = df.copy()
    df_temp['order_date'] = pd.to_datetime(df_temp['order_date'])
    df_temp['year_month'] = df_temp['order_date'].dt.to_period('M').astype(str)

    monthly = df_temp.groupby('year_month').agg(
        gross_revenue=('gross_revenue', 'sum'),
        net_revenue=('net_revenue', 'sum'),
        product_cost=('product_cost', 'sum'),
        margin=('margin', 'sum'),
        orders=('order_id', 'nunique'),
        customers=('customer_id', 'nunique'),
        units=('quantity', 'sum'),
        discount_amount=('discount_amount', 'sum')
    ).reset_index()

    monthly['gross_margin_pct'] = (monthly['margin'] / monthly['net_revenue']).round(4)
    monthly['aov'] = (monthly['net_revenue'] / monthly['orders']).round(2)
    monthly['mom_revenue_growth'] = monthly['net_revenue'].pct_change().round(4)
    monthly['rolling_3m_revenue'] = monthly['net_revenue'].rolling(window=3, min_periods=1).mean().round(2)

    return monthly

def compute_pareto_analysis(df: pd.DataFrame, group_col: str, value_col: str = 'net_revenue') -> Dict[str, Any]:
    """
    Performs rigorous 80/20 Pareto analysis on any dimension.
    Returns ranked breakdown, cumulative shares, and threshold counts.
    """
    grouped = df.groupby(group_col)[value_col].sum().reset_index()
    grouped = grouped.sort_values(by=value_col, ascending=False).reset_index(drop=True)

    total_val = grouped[value_col].sum()
    if total_val == 0:
        return {'table': grouped, 'threshold_counts': {}, 'shares': {}}

    grouped['share'] = (grouped[value_col] / total_val).round(4)
    grouped['cumulative_value'] = grouped[value_col].cumsum().round(2)
    grouped['cumulative_share'] = (grouped['cumulative_value'] / total_val).round(4)
    grouped['rank'] = grouped.index + 1

    n_entities = len(grouped)

    # Calculate Top 1, 3, 5, 10 shares
    top_shares = {
        'top_1_share': round(float(grouped.loc[0, 'share']) if n_entities >= 1 else 0.0, 4),
        'top_3_share': round(float(grouped.loc[:2, 'share'].sum()) if n_entities >= 3 else float(grouped['share'].sum()), 4),
        'top_5_share': round(float(grouped.loc[:4, 'share'].sum()) if n_entities >= 5 else float(grouped['share'].sum()), 4),
        'top_10_share': round(float(grouped.loc[:9, 'share'].sum()) if n_entities >= 10 else float(grouped['share'].sum()), 4),
    }

    # Number of entities required to hit 50%, 70%, 80%, 90%
    threshold_counts = {}
    for t in PARETO_THRESHOLDS:
        pct_label = f"{int(t * 100)}%"
        passing = grouped[grouped['cumulative_share'] >= t]
        if not passing.empty:
            threshold_counts[pct_label] = int(passing.iloc[0]['rank'])
        else:
            threshold_counts[pct_label] = n_entities

    return {
        'table': grouped,
        'total_entities': n_entities,
        'top_shares': top_shares,
        'threshold_counts': threshold_counts
    }
