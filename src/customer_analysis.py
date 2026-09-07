"""
Customer Analytics Module.
Calculates RFM segmentation, customer lifetime metrics, repeat purchase rates,
monthly cohort retention, and fulfillment impact on repeat behavior.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple

def compute_rfm_segmentation(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes Recency, Frequency, Monetary (RFM) segmentation for all customers.
    Segments into Champions, Loyal Customers, Potential Loyalists, At Risk, and Dormant.
    """
    reference_date = pd.to_datetime(df['order_date']).max() + pd.Timedelta(days=1)

    rfm = df.groupby('customer_id').agg(
        recency=('order_date', lambda x: (reference_date - pd.to_datetime(x).max()).days),
        frequency=('order_id', 'nunique'),
        monetary=('net_revenue', 'sum'),
        first_order_date=('order_date', 'min'),
        last_order_date=('order_date', 'max'),
        avg_transit_days=('transit_days', 'mean'),
        return_rate=('return_flag', 'mean')
    ).reset_index()

    rfm['aov'] = (rfm['monetary'] / rfm['frequency']).round(2)

    # RFM Scoring using quantiles (1 to 5)
    rfm['R_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop').astype(int)
    rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['M_score'] = pd.qcut(rfm['monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)

    def assign_segment(row):
        r, f, m = row['R_score'], row['F_score'], row['M_score']
        if r >= 4 and f >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal Customers'
        elif r >= 3 and f <= 2:
            return 'Potential Loyalists'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'Dormant'
        else:
            return 'Promising'

    rfm['segment'] = rfm.apply(assign_segment, axis=1)

    summary = rfm.groupby('segment').agg(
        customer_count=('customer_id', 'count'),
        avg_recency=('recency', 'mean'),
        avg_frequency=('frequency', 'mean'),
        avg_monetary=('monetary', 'mean'),
        total_revenue=('monetary', 'sum')
    ).round(2).reset_index()

    summary['revenue_share'] = (summary['total_revenue'] / rfm['monetary'].sum()).round(4)
    summary = summary.sort_values(by='total_revenue', ascending=False).reset_index(drop=True)

    return rfm, summary.to_dict(orient='records')

def compute_cohort_retention(df: pd.DataFrame) -> pd.DataFrame:
    """Computes monthly customer cohort retention matrix."""
    df_temp = df.copy()
    df_temp['order_date'] = pd.to_datetime(df_temp['order_date'])
    df_temp['order_month'] = df_temp['order_date'].dt.to_period('M')

    # Determine first order month per customer
    df_temp['cohort'] = df_temp.groupby('customer_id')['order_month'].transform('min')

    # Calculate cohort index (period difference in months)
    def month_diff(period_a, period_b):
        return (period_a.dt.year - period_b.dt.year) * 12 + (period_a.dt.month - period_b.dt.month)

    df_temp['cohort_index'] = month_diff(df_temp['order_month'], df_temp['cohort'])

    cohort_data = df_temp.groupby(['cohort', 'cohort_index'])['customer_id'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='cohort', columns='cohort_index', values='customer_id')

    cohort_sizes = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_sizes, axis=0).round(4)

    return retention_matrix

def analyze_transit_vs_repeat_purchasing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates association between customer-level transit performance
    and subsequent repeat purchasing behavior.
    """
    cust_orders = df.sort_values(['customer_id', 'order_date']).groupby('customer_id')
    first_orders = cust_orders.first().reset_index()
    order_counts = df.groupby('customer_id')['order_id'].nunique().reset_index(name='total_orders')
    first_orders = first_orders.merge(order_counts, on='customer_id')
    first_orders['is_repeat_customer'] = (first_orders['total_orders'] > 1).astype(int)

    first_orders['transit_group'] = pd.cut(
        first_orders['transit_days'],
        bins=[-np.inf, 3, 5, np.inf],
        labels=['Fast (1-3 Days)', 'Standard (4-5 Days)', 'Delayed (6+ Days)']
    )

    transit_impact = first_orders.groupby('transit_group', observed=False).agg(
        customers=('customer_id', 'count'),
        repeat_rate=('is_repeat_customer', 'mean'),
        avg_total_orders=('total_orders', 'mean')
    ).reset_index()
    transit_impact['repeat_rate'] = transit_impact['repeat_rate'].round(4)
    transit_impact['avg_total_orders'] = transit_impact['avg_total_orders'].round(2)

    return transit_impact
