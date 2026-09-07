"""
Analytical Feature Engineering Module.
Creates revenue, margin, discount, temporal, logistics, and customer features.
Prevents data leakage by respecting chronological order.
"""
import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes business and operational features on cleaned transactional data."""
    df = df.copy()

    # 1. Temporal Features
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['order_year'] = df['order_date'].dt.year
    df['order_quarter'] = df['order_date'].dt.to_period('Q').astype(str)
    df['order_month'] = df['order_date'].dt.to_period('M').astype(str)
    df['order_day'] = df['order_date'].dt.day_name()

    # 2. Financial Metrics
    # Discount Rate = discount_amount / gross_revenue
    df['discount_rate'] = np.where(
        df['gross_revenue'] > 0,
        (df['discount_amount'] / df['gross_revenue']).round(4),
        0.0
    )

    # Gross Margin % = margin / net_revenue
    df['margin_rate'] = np.where(
        df['net_revenue'] > 0,
        (df['margin'] / df['net_revenue']).round(4),
        0.0
    )

    # 3. Logistics & Fulfillment Features
    if 'transit_days' not in df.columns or df['transit_days'].isnull().all():
        if 'delivery_date' in df.columns and 'shipping_date' in df.columns:
            df['transit_days'] = (pd.to_datetime(df['delivery_date']) - pd.to_datetime(df['shipping_date'])).dt.days

    # Transit time buckets for statistical grouping
    df['transit_bucket'] = pd.cut(
        df['transit_days'],
        bins=[-np.inf, 2, 4, 6, np.inf],
        labels=['1-2 Days (Fast)', '3-4 Days (Standard)', '5-6 Days (Delayed)', '7+ Days (Severe Delay)']
    )

    df['is_delayed'] = np.where(df['transit_days'] > 5, 1, 0)

    # 4. Customer-Level Historical Order Sequence (Leakage-free)
    df = df.sort_values(by=['customer_id', 'order_date', 'order_id']).reset_index(drop=True)
    df['customer_order_rank'] = df.groupby('customer_id').cumcount() + 1
    df['is_repeat_order'] = np.where(df['customer_order_rank'] > 1, 1, 0)

    return df
