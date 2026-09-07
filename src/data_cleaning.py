"""
Data Cleaning and Quality Assurance Module.
Performs schema validation, duplicate removal, invalid record filtration,
string normalization, financial reconciliation, and data quality profiling.
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Tuple, Dict, Any
from src.config import TOLERANCE, REPORTS_DIR

def inspect_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """Inspects column types, memory usage, and null counts."""
    return {
        'total_rows': int(len(df)),
        'total_columns': int(df.shape[1]),
        'columns': {
            col: {
                'dtype': str(df[col].dtype),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': round(float(df[col].isnull().mean() * 100), 2),
                'unique_values': int(df[col].nunique())
            }
            for col in df.columns
        }
    }

def clean_data(raw_orders: pd.DataFrame, raw_customers: pd.DataFrame = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes end-to-end data cleaning pipeline.
    Returns cleaned DataFrame and Data Quality report dictionary.
    """
    initial_rows = len(raw_orders)
    df = raw_orders.copy()

    # 1. Duplicate Detection & Removal
    dup_mask = df.duplicated()
    dup_count = int(dup_mask.sum())
    df = df.drop_duplicates().reset_index(drop=True)

    # 2. Invalidation Filtration: Non-positive quantities
    bad_qty_mask = df['quantity'] <= 0
    invalid_qty_count = int(bad_qty_mask.sum())
    df = df[~bad_qty_mask].reset_index(drop=True)

    # 3. String & Categorical Normalization
    text_cols = ['region', 'category', 'subcategory', 'brand', 'state', 'city']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Normalize category capitalization specifically
    category_map = {
        'Electronics': 'Electronics',
        'Apparel & Fashion': 'Apparel & Fashion',
        'Home & Kitchen': 'Home & Kitchen',
        'Health & Beauty': 'Health & Beauty',
        'Sports & Outdoors': 'Sports & Outdoors'
    }
    df['category'] = df['category'].replace({k.title(): v for k, v in category_map.items()})

    # 4. Datetime Parsing
    date_cols = ['order_date', 'shipping_date', 'delivery_date']
    for c in date_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')

    # 5. Financial Validation & Recalculation
    # gross_revenue = quantity * unit_price
    expected_gross = df['quantity'] * df['unit_price']
    gross_discrepancy = (df['gross_revenue'] - expected_gross).abs() > TOLERANCE
    df['gross_revenue'] = expected_gross.round(2)

    # net_revenue = gross_revenue - discount_amount
    expected_net = (df['gross_revenue'] - df['discount_amount']).clip(lower=0.0)
    df['net_revenue'] = expected_net.round(2)

    # margin = net_revenue - product_cost
    df['margin'] = (df['net_revenue'] - df['product_cost']).round(2)

    # 6. Optional Customer Table Joining
    if raw_customers is not None:
        cust_df = raw_customers.drop_duplicates(subset=['customer_id']).copy()
        if 'customer_segment' not in df.columns and 'customer_segment' in cust_df.columns:
            df = df.merge(cust_df[['customer_id', 'customer_segment', 'acquisition_channel']], on='customer_id', how='left')

    final_rows = len(df)

    # Data Quality Report
    dq_report = {
        'initial_rows': initial_rows,
        'final_rows': final_rows,
        'duplicates_removed': dup_count,
        'invalid_records_removed': invalid_qty_count,
        'gross_discrepancies_corrected': int(gross_discrepancy.sum()),
        'date_range': {
            'min_order_date': str(df['order_date'].min().strftime('%Y-%m-%d')),
            'max_order_date': str(df['order_date'].max().strftime('%Y-%m-%d'))
        },
        'uniques': {
            'unique_orders': int(df['order_id'].nunique()) if 'order_id' in df.columns else 0,
            'unique_customers': int(df['customer_id'].nunique()) if 'customer_id' in df.columns else 0,
            'unique_products': int(df['product_id'].nunique()) if 'product_id' in df.columns else 0,
            'unique_brands': int(df['brand'].nunique()) if 'brand' in df.columns else 0,
            'unique_categories': int(df['category'].nunique()) if 'category' in df.columns else 0,
            'unique_regions': int(df['region'].nunique()) if 'region' in df.columns else 0
        },
        'null_summary': {col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().sum() > 0}
    }

    # Save Data Quality Report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / 'data_quality_report.json', 'w', encoding='utf-8') as f:
        json.dump(dq_report, f, indent=2)

    return df, dq_report
