"""
Brand Portfolio Analytics Module.
Calculates brand revenue concentration, margin distribution, customer reach,
and classifies brands into Anchor, Growth, Margin, and Risk profiles.
"""
import pandas as pd
import numpy as np
from src.config import BRAND_VOLUME_QUANTILE, BRAND_HIGH_GROWTH_THRESHOLD, BRAND_HIGH_MARGIN_THRESHOLD

def compute_brand_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Computes comprehensive brand KPIs and quantitative strategic profiles."""
    total_net = df['net_revenue'].sum()

    brand_df = df.groupby('brand').agg(
        category=('category', 'first'),
        net_revenue=('net_revenue', 'sum'),
        gross_revenue=('gross_revenue', 'sum'),
        margin=('margin', 'sum'),
        orders=('order_id', 'nunique'),
        customers=('customer_id', 'nunique'),
        units=('quantity', 'sum'),
        return_flag=('return_flag', 'mean'),
        dispute_flag=('dispute_flag', 'mean'),
        discount_amount=('discount_amount', 'sum')
    ).reset_index()

    brand_df['revenue_share'] = (brand_df['net_revenue'] / total_net).round(4)
    brand_df['gross_margin_pct'] = (brand_df['margin'] / brand_df['net_revenue']).round(4)
    brand_df['aov'] = (brand_df['net_revenue'] / brand_df['orders']).round(2)
    brand_df['return_rate'] = brand_df['return_flag'].round(4)
    brand_df['dispute_rate'] = brand_df['dispute_flag'].round(4)
    brand_df['discount_rate'] = (brand_df['discount_amount'] / brand_df['gross_revenue']).round(4)

    # YoY Growth per brand
    df_temp = df.copy()
    df_temp['order_year'] = pd.to_datetime(df_temp['order_date']).dt.year
    brand_yearly = df_temp.groupby(['brand', 'order_year'])['net_revenue'].sum().unstack(fill_value=0)
    if 2023 in brand_yearly.columns and 2024 in brand_yearly.columns:
        growth = ((brand_yearly[2024] - brand_yearly[2023]) / brand_yearly[2023]).round(4).reset_index()
        growth.columns = ['brand', 'growth_rate']
        brand_df = brand_df.merge(growth, on='brand', how='left')
    else:
        brand_df['growth_rate'] = 0.0

    # Quantitative Classification Rules
    vol_threshold = brand_df['units'].quantile(BRAND_VOLUME_QUANTILE)
    share_threshold = brand_df['revenue_share'].quantile(BRAND_VOLUME_QUANTILE)
    median_growth = brand_df['growth_rate'].median()

    def classify_brand(row):
        # Anchor Brands: High Volume, high customer reach, top revenue share
        if row['units'] >= vol_threshold and row['revenue_share'] >= share_threshold and row['gross_margin_pct'] >= 0.25:
            return 'Anchor Brand'
        # Risk Brands: High revenue/volume but low margin or elevated return rate
        elif (row['revenue_share'] >= share_threshold and row['gross_margin_pct'] < 0.25) or row['return_rate'] > 0.10:
            return 'Risk Brand'
        # Margin Brands: High profitability
        elif row['gross_margin_pct'] >= BRAND_HIGH_MARGIN_THRESHOLD:
            return 'Margin Brand'
        # Growth Brands: High growth rate
        elif row['growth_rate'] >= median_growth:
            return 'Growth Brand'
        else:
            return 'Core Portfolio'

    brand_df['portfolio_classification'] = brand_df.apply(classify_brand, axis=1)

    return brand_df.sort_values(by='net_revenue', ascending=False).reset_index(drop=True)
