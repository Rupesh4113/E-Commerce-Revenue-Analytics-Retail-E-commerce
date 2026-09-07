"""
Unit tests for data cleaning and schema validation.
"""
import pytest
import pandas as pd
import numpy as np
from src.data_cleaning import clean_data, inspect_schema

@pytest.fixture
def sample_raw_orders():
    return pd.DataFrame({
        'order_id': ['ORD-1', 'ORD-2', 'ORD-2', 'ORD-3', 'ORD-4'],
        'customer_id': ['C-1', 'C-2', 'C-2', 'C-3', 'C-4'],
        'order_date': ['2024-01-01', '2024-01-02', '2024-01-02', '2024-01-03', '2024-01-04'],
        'product_id': ['P-1', 'P-2', 'P-2', 'P-3', 'P-4'],
        'product_name': ['Item A', 'Item B', 'Item B', 'Item C', 'Item D'],
        'quantity': [2, 1, 1, 0, -3],
        'unit_price': [100.0, 50.0, 50.0, 80.0, 20.0],
        'gross_revenue': [200.0, 50.0, 50.0, 0.0, -60.0],
        'discount_amount': [20.0, 0.0, 0.0, 0.0, 0.0],
        'net_revenue': [180.0, 50.0, 50.0, 0.0, -60.0],
        'product_cost': [120.0, 30.0, 30.0, 40.0, 10.0],
        'margin': [60.0, 20.0, 20.0, -40.0, -70.0],
        'region': [' north ', 'South', 'South', 'EAST', 'west'],
        'category': ['electronics', 'Fashion', 'Fashion', 'ELECTRONICS', 'Home & Kitchen'],
        'brand': ['TechNova', 'UrbanChic', 'UrbanChic', 'AuraHome', 'ZenFit']
    })

def test_duplicate_removal(sample_raw_orders):
    cleaned, dq = clean_data(sample_raw_orders)
    assert dq['duplicates_removed'] == 1
    assert len(cleaned[cleaned['order_id'] == 'ORD-2']) == 1

def test_invalid_quantity_handling(sample_raw_orders):
    cleaned, dq = clean_data(sample_raw_orders)
    assert dq['invalid_records_removed'] == 2
    assert (cleaned['quantity'] > 0).all()

def test_string_normalization(sample_raw_orders):
    cleaned, _ = clean_data(sample_raw_orders)
    assert 'North' in cleaned['region'].values
    assert ' north ' not in cleaned['region'].values
    assert 'Electronics' in cleaned['category'].values

def test_financial_recalculation(sample_raw_orders):
    cleaned, _ = clean_data(sample_raw_orders)
    row = cleaned[cleaned['order_id'] == 'ORD-1'].iloc[0]
    assert row['gross_revenue'] == 200.0
    assert row['net_revenue'] == 180.0
    assert row['margin'] == 60.0

def test_schema_inspection(sample_raw_orders):
    schema = inspect_schema(sample_raw_orders)
    assert schema['total_rows'] == 5
    assert 'quantity' in schema['columns']
