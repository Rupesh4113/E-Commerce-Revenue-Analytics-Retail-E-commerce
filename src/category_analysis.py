"""
Category and Product Analytics Module.
Evaluates category economics, volume vs margin profiles, discount elasticity,
and cross-sell affinity (bundling analysis).
"""
import pandas as pd
import numpy as np
from itertools import combinations
from collections import Counter
from typing import Dict, Any, List

def compute_category_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Computes category-level economics and strategic classifications."""
    total_net = df['net_revenue'].sum()
    total_margin = df['margin'].sum()

    cat_df = df.groupby('category').agg(
        net_revenue=('net_revenue', 'sum'),
        gross_revenue=('gross_revenue', 'sum'),
        margin=('margin', 'sum'),
        orders=('order_id', 'nunique'),
        units=('quantity', 'sum'),
        discount_amount=('discount_amount', 'sum'),
        return_flag=('return_flag', 'mean')
    ).reset_index()

    cat_df['revenue_share'] = (cat_df['net_revenue'] / total_net).round(4)
    cat_df['margin_contribution'] = (cat_df['margin'] / total_margin).round(4)
    cat_df['gross_margin_pct'] = (cat_df['margin'] / cat_df['net_revenue']).round(4)
    cat_df['aov'] = (cat_df['net_revenue'] / cat_df['orders']).round(2)
    cat_df['discount_rate'] = (cat_df['discount_amount'] / cat_df['gross_revenue']).round(4)
    cat_df['return_rate'] = cat_df['return_flag'].round(4)

    # YoY Growth per category
    df_temp = df.copy()
    df_temp['order_year'] = pd.to_datetime(df_temp['order_date']).dt.year
    cat_yearly = df_temp.groupby(['category', 'order_year'])['net_revenue'].sum().unstack(fill_value=0)
    if 2023 in cat_yearly.columns and 2024 in cat_yearly.columns:
        growth = ((cat_yearly[2024] - cat_yearly[2023]) / cat_yearly[2023]).round(4).reset_index()
        growth.columns = ['category', 'growth_rate']
        cat_df = cat_df.merge(growth, on='category', how='left')
    else:
        cat_df['growth_rate'] = 0.0

    # Multi-dimensional Category Classification
    median_margin = cat_df['gross_margin_pct'].median()
    median_rev = cat_df['net_revenue'].median()
    median_units = cat_df['units'].median()

    def classify_category(row):
        if row['net_revenue'] >= median_rev and row['gross_margin_pct'] >= median_margin:
            return 'Margin & Revenue Leader'
        elif row['net_revenue'] >= median_rev and row['gross_margin_pct'] < median_margin:
            return 'Volume Driver (High Vol / Lower Margin)'
        elif row['gross_margin_pct'] >= median_margin:
            return 'Margin Specialist (Niche High Profit)'
        elif row['discount_rate'] > 0.08:
            return 'Discount-Dependent'
        else:
            return 'Underperformer'

    cat_df['classification'] = cat_df.apply(classify_category, axis=1)

    return cat_df.sort_values(by='net_revenue', ascending=False).reset_index(drop=True)

def compute_market_basket_bundling(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Identifies frequently co-purchased subcategories across customer baskets
    to formulate data-driven bundling recommendations.
    """
    # Group subcategories by customer and order_date
    baskets = df.groupby(['customer_id', 'order_date'])['subcategory'].unique()
    multi_item_baskets = [b for b in baskets if len(b) > 1]

    pair_counts = Counter()
    for basket in multi_item_baskets:
        pairs = combinations(sorted(basket), 2)
        pair_counts.update(pairs)

    if not pair_counts:
        # Fallback to category level pairing
        cat_baskets = df.groupby(['customer_id', 'order_date'])['category'].unique()
        multi_cat = [b for b in cat_baskets if len(b) > 1]
        for basket in multi_cat:
            pair_counts.update(combinations(sorted(basket), 2))

    records = []
    total_baskets = max(1, len(multi_item_baskets))
    for (item_a, item_b), count in pair_counts.most_common(top_n):
        records.append({
            'item_a': item_a,
            'item_b': item_b,
            'bundle_candidate': f"{item_a} + {item_b}",
            'co_occurrence_count': count,
            'support_rate': round(count / total_baskets, 4),
            'recommended_strategy': 'Bundle anchor volume driver with complementary high-margin accessory'
        })

    return pd.DataFrame(records)
