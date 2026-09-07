"""
Configuration module for E-Commerce Revenue Analytics.
Centralizes paths, random seeds, reconciliation thresholds, and business rules.
"""
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
OUTPUTS_DIR = BASE_DIR / 'outputs'
FIGURES_DIR = OUTPUTS_DIR / 'figures'
REPORTS_DIR = OUTPUTS_DIR / 'reports'
TABLES_DIR = OUTPUTS_DIR / 'tables'

# Ensure directories exist
for p in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, REPORTS_DIR, TABLES_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Reproducibility Seed
RANDOM_SEED = 42

# Numerical Reconciliation Tolerance (Floating point precision)
TOLERANCE = 1e-4

# Pareto Cumulative Thresholds
PARETO_THRESHOLDS = [0.50, 0.70, 0.80, 0.90]

# Brand Quantitative Classification Parameters
BRAND_VOLUME_QUANTILE = 0.65
BRAND_HIGH_GROWTH_THRESHOLD = 0.10
BRAND_HIGH_MARGIN_THRESHOLD = 0.35

# Expected Raw Orders Schema
EXPECTED_ORDERS_COLUMNS = [
    'order_id', 'customer_id', 'order_date', 'product_id', 'product_name',
    'quantity', 'unit_price', 'gross_revenue', 'discount_amount',
    'net_revenue', 'product_cost', 'margin', 'region', 'state', 'city',
    'category', 'subcategory', 'brand', 'shipping_date', 'delivery_date',
    'delivery_status', 'return_flag', 'dispute_flag', 'logistics_hub',
    'transit_days', 'shipping_cost'
]
