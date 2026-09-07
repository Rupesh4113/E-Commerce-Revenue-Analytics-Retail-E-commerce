"""
Regional Analytics Module.
Calculates geographic performance metrics, logistics corridor efficiency,
and implements the 2x2 Regional Opportunity Matrix.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

def compute_regional_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Computes key commercial and operational metrics aggregated by region."""
    total_net = df['net_revenue'].sum()

    regional = df.groupby('region').agg(
        net_revenue=('net_revenue', 'sum'),
        gross_revenue=('gross_revenue', 'sum'),
        margin=('margin', 'sum'),
        orders=('order_id', 'nunique'),
        customers=('customer_id', 'nunique'),
        units=('quantity', 'sum'),
        discount_amount=('discount_amount', 'sum'),
        return_flag=('return_flag', 'mean'),
        dispute_flag=('dispute_flag', 'mean'),
        transit_days=('transit_days', 'mean'),
        shipping_cost=('shipping_cost', 'mean')
    ).reset_index()

    regional['revenue_share'] = (regional['net_revenue'] / total_net).round(4)
    regional['gross_margin_pct'] = (regional['margin'] / regional['net_revenue']).round(4)
    regional['aov'] = (regional['net_revenue'] / regional['orders']).round(2)
    regional['revenue_per_customer'] = (regional['net_revenue'] / regional['customers']).round(2)
    regional['return_rate'] = regional['return_flag'].round(4)
    regional['dispute_rate'] = regional['dispute_flag'].round(4)
    regional['avg_transit_days'] = regional['transit_days'].round(2)
    regional['avg_shipping_cost'] = regional['shipping_cost'].round(2)

    # Compute Regional Growth (comparing 2024 vs 2023 revenue)
    df_temp = df.copy()
    df_temp['order_year'] = pd.to_datetime(df_temp['order_date']).dt.year
    reg_yearly = df_temp.groupby(['region', 'order_year'])['net_revenue'].sum().unstack(fill_value=0)
    
    if 2023 in reg_yearly.columns and 2024 in reg_yearly.columns:
        growth = ((reg_yearly[2024] - reg_yearly[2023]) / reg_yearly[2023]).round(4).reset_index()
        growth.columns = ['region', 'growth_rate']
        regional = regional.merge(growth, on='region', how='left')
    else:
        regional['growth_rate'] = 0.0

    # Classify into Regional Opportunity Matrix (2x2)
    median_rev = regional['net_revenue'].median()
    median_growth = regional['growth_rate'].median()

    def classify_region(row):
        high_rev = row['net_revenue'] >= median_rev
        high_growth = row['growth_rate'] >= median_growth
        if high_rev and high_growth:
            return 'Defend & Scale (High Rev, High Growth)'
        elif high_rev and not high_growth:
            return 'Retention & Optimization (High Rev, Low Growth)'
        elif not high_rev and high_growth:
            return 'Expansion Opportunity (Low Rev, High Growth)'
        else:
            return 'Controlled Investment (Low Rev, Low Growth)'

    regional['opportunity_classification'] = regional.apply(classify_region, axis=1)

    return regional.sort_values(by='net_revenue', ascending=False).reset_index(drop=True)
