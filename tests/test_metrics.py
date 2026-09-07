"""
Unit tests for financial metrics, aggregations, Pareto curves, and reconciliation rules.
"""
import pytest
import pandas as pd
import numpy as np
from src.revenue_analysis import compute_executive_kpis, compute_pareto_analysis
from src.regional_analysis import compute_regional_performance
from src.category_analysis import compute_category_performance
from src.brand_analysis import compute_brand_performance
from src.config import TOLERANCE

@pytest.fixture
def analytical_dataset():
    from src.data_loader import load_processed_data
    return load_processed_data()

def test_revenue_and_margin_formulas(analytical_dataset):
    df = analytical_dataset
    expected_gross = df['quantity'] * df['unit_price']
    diff_gross = (df['gross_revenue'] - expected_gross).abs()
    assert (diff_gross <= 0.05).all()

    expected_net = df['gross_revenue'] - df['discount_amount']
    diff_net = (df['net_revenue'] - expected_net).abs()
    assert (diff_net <= 0.05).all()

    expected_margin = df['net_revenue'] - df['product_cost']
    diff_margin = (df['margin'] - expected_margin).abs()
    assert (diff_margin <= 0.05).all()

def test_reconciliation_totals(analytical_dataset):
    df = analytical_dataset
    kpis = compute_executive_kpis(df)
    total_net = kpis['total_net_revenue']

    reg_df = compute_regional_performance(df)
    assert pytest.approx(reg_df['net_revenue'].sum(), abs=1.0) == total_net
    assert pytest.approx(reg_df['revenue_share'].sum(), abs=0.01) == 1.0

    cat_df = compute_category_performance(df)
    assert pytest.approx(cat_df['net_revenue'].sum(), abs=1.0) == total_net
    assert pytest.approx(cat_df['revenue_share'].sum(), abs=0.01) == 1.0

    brand_df = compute_brand_performance(df)
    assert pytest.approx(brand_df['net_revenue'].sum(), abs=1.0) == total_net
    assert pytest.approx(brand_df['revenue_share'].sum(), abs=0.01) == 1.0

def test_aov_reconciliation(analytical_dataset):
    df = analytical_dataset
    kpis = compute_executive_kpis(df)
    
    order_sums = df.groupby('order_id')['net_revenue'].sum()
    expected_aov = order_sums.mean()
    assert pytest.approx(kpis['aov'], 0.01) == round(float(expected_aov), 2)

def test_pareto_monotonicity(analytical_dataset):
    df = analytical_dataset
    pareto_brand = compute_pareto_analysis(df, group_col='brand')
    table = pareto_brand['table']
    
    revenues = table['net_revenue'].values
    assert (np.diff(revenues) <= 0).all()
    assert pytest.approx(table['cumulative_share'].iloc[-1], abs=0.01) == 1.0

def test_brand_classifications_exist(analytical_dataset):
    df = analytical_dataset
    brand_df = compute_brand_performance(df)
    classifications = brand_df['portfolio_classification'].unique()
    assert len(classifications) >= 2
