"""
Unit tests for feature engineering calculations.
"""
import pytest
import pandas as pd
import numpy as np
from src.feature_engineering import engineer_features

@pytest.fixture
def sample_cleaned_df():
    return pd.DataFrame({
        'order_id': ['ORD-1', 'ORD-2', 'ORD-3'],
        'customer_id': ['C-1', 'C-1', 'C-2'],
        'order_date': ['2023-05-10', '2023-08-15', '2024-01-20'],
        'quantity': [2, 1, 3],
        'unit_price': [100.0, 200.0, 50.0],
        'gross_revenue': [200.0, 200.0, 150.0],
        'discount_amount': [20.0, 0.0, 15.0],
        'net_revenue': [180.0, 200.0, 135.0],
        'product_cost': [100.0, 120.0, 80.0],
        'margin': [80.0, 80.0, 55.0],
        'shipping_date': ['2023-05-11', '2023-08-16', '2024-01-21'],
        'delivery_date': ['2023-05-14', '2023-08-19', '2024-01-28'],
        'transit_days': [3, 3, 7]
    })

def test_discount_rate_calculation(sample_cleaned_df):
    df_feat = engineer_features(sample_cleaned_df)
    row_1 = df_feat[df_feat['order_id'] == 'ORD-1'].iloc[0]
    assert pytest.approx(row_1['discount_rate'], 1e-4) == 0.1000
    row_2 = df_feat[df_feat['order_id'] == 'ORD-2'].iloc[0]
    assert row_2['discount_rate'] == 0.0

def test_margin_rate_calculation(sample_cleaned_df):
    df_feat = engineer_features(sample_cleaned_df)
    row_1 = df_feat[df_feat['order_id'] == 'ORD-1'].iloc[0]
    assert pytest.approx(row_1['margin_rate'], 1e-3) == 0.4444

def test_transit_bucket_and_delay(sample_cleaned_df):
    df_feat = engineer_features(sample_cleaned_df)
    row_3 = df_feat[df_feat['order_id'] == 'ORD-3'].iloc[0]
    assert row_3['is_delayed'] == 1

def test_repeat_order_sequencing(sample_cleaned_df):
    df_feat = engineer_features(sample_cleaned_df)
    c1_orders = df_feat[df_feat['customer_id'] == 'C-1'].sort_values('order_date')
    assert c1_orders.iloc[0]['is_repeat_order'] == 0
    assert c1_orders.iloc[1]['is_repeat_order'] == 1
