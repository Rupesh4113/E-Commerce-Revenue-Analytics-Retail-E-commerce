"""
Master Pipeline Orchestration Runner.
Runs the entire analytical pipeline end-to-end:
Data generation -> Ingestion -> Cleaning & QA -> Feature Engineering -> Analytics -> Output Generation.
"""
import sys
from pathlib import Path
import json
import pandas as pd

# Add root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUTS_DIR, TABLES_DIR, REPORTS_DIR, FIGURES_DIR
from src.data_generator import generate_dataset
from src.data_loader import load_raw_orders, load_raw_customers, load_raw_products, load_raw_logistics
from src.data_cleaning import clean_data, inspect_schema
from src.feature_engineering import engineer_features
from src.revenue_analysis import compute_executive_kpis, compute_temporal_trends, compute_pareto_analysis
from src.regional_analysis import compute_regional_performance
from src.category_analysis import compute_category_performance, compute_market_basket_bundling
from src.brand_analysis import compute_brand_performance
from src.customer_analysis import compute_rfm_segmentation, compute_cohort_retention, analyze_transit_vs_repeat_purchasing
from src.statistical_analysis import compute_descriptive_statistics, compute_correlation_analysis, perform_inferential_tests
from src.insights import generate_executive_insights, generate_business_recommendations
from src.visualization import (
    plot_monthly_revenue_trend, plot_regional_revenue_bar, plot_regional_revenue_donut,
    plot_pareto_curve, plot_category_revenue_margin, plot_brand_risk_matrix,
    plot_regional_opportunity_matrix, plot_transit_vs_repeat, plot_rfm_segments, plot_cohort_retention
)

def run_pipeline():
    print("=" * 70)
    print("STARTING E-COMMERCE REVENUE ANALYTICS PIPELINE")
    print("=" * 70)

    # 1. Ensure Raw Data Exists
    if not (RAW_DATA_DIR / 'orders.csv').exists():
        print("[Step 1] Generating raw synthetic dataset...")
        generate_dataset()
    else:
        print("[Step 1] Found existing raw dataset in data/raw/.")

    # 2. Ingest Raw Tables
    print("[Step 2] Ingesting raw transactional and dimension tables...")
    raw_orders = load_raw_orders()
    raw_customers = load_raw_customers()
    raw_products = load_raw_products()
    raw_logistics = load_raw_logistics()
    print(f"  Raw Orders: {len(raw_orders):,} rows | Raw Customers: {len(raw_customers):,} rows")

    # Initial Schema Inspection
    schema_info = inspect_schema(raw_orders)
    with open(REPORTS_DIR / 'raw_schema_inspection.json', 'w', encoding='utf-8') as f:
        json.dump(schema_info, f, indent=2)

    # 3. Clean Data & Validate Integrity
    print("[Step 3] Cleaning data and executing QA validations...")
    cleaned_df, dq_report = clean_data(raw_orders, raw_customers)
    print(f"  Initial Rows: {dq_report['initial_rows']:,} | Final Clean Rows: {dq_report['final_rows']:,}")
    print(f"  Removed {dq_report['duplicates_removed']} duplicates and {dq_report['invalid_records_removed']} invalid records.")

    # 4. Feature Engineering
    print("[Step 4] Engineering analytical, temporal, financial, and customer features...")
    analytical_df = engineer_features(cleaned_df)
    
    # Save Processed Dataset
    processed_path = PROCESSED_DATA_DIR / 'ecommerce_analytical_dataset.csv'
    analytical_df.to_csv(processed_path, index=False)
    print(f"  Saved analytical dataset ({len(analytical_df):,} records) to {processed_path}")

    # 5. Core Analytical Computations
    print("[Step 5] Computing revenue, regional, category, brand, and customer analytics...")
    
    # Executive KPIs
    kpis = compute_executive_kpis(analytical_df)
    with open(REPORTS_DIR / 'executive_kpis.json', 'w', encoding='utf-8') as f:
        json.dump(kpis, f, indent=2)
    print(f"  Total Net Revenue: ${kpis['total_net_revenue']:,.2f} | AOV: ${kpis['aov']:,.2f} | Margin: {kpis['gross_margin_pct']*100:.1f}%")

    # Temporal Trends
    monthly_trends = compute_temporal_trends(analytical_df)
    monthly_trends.to_csv(TABLES_DIR / 'monthly_revenue_trends.csv', index=False)

    # Pareto Concentration Analyses
    pareto_brand = compute_pareto_analysis(analytical_df, group_col='brand')
    pareto_cat = compute_pareto_analysis(analytical_df, group_col='category')
    pareto_region = compute_pareto_analysis(analytical_df, group_col='region')
    pareto_brand['table'].to_csv(TABLES_DIR / 'pareto_brand_analysis.csv', index=False)
    pareto_cat['table'].to_csv(TABLES_DIR / 'pareto_category_analysis.csv', index=False)
    pareto_region['table'].to_csv(TABLES_DIR / 'pareto_region_analysis.csv', index=False)

    # Regional Performance
    regional_df = compute_regional_performance(analytical_df)
    regional_df.to_csv(TABLES_DIR / 'regional_performance.csv', index=False)

    # Category Performance & Market Basket Bundling
    cat_df = compute_category_performance(analytical_df)
    cat_df.to_csv(TABLES_DIR / 'category_performance.csv', index=False)
    bundling_df = compute_market_basket_bundling(analytical_df)
    bundling_df.to_csv(TABLES_DIR / 'product_bundling_candidates.csv', index=False)

    # Brand Portfolio
    brand_df = compute_brand_performance(analytical_df)
    brand_df.to_csv(TABLES_DIR / 'brand_performance.csv', index=False)

    # Customer Analytics: RFM, Cohorts, and Transit Impact
    rfm_df, rfm_summary = compute_rfm_segmentation(analytical_df)
    rfm_df.to_csv(TABLES_DIR / 'customer_rfm_scores.csv', index=False)
    pd.DataFrame(rfm_summary).to_csv(TABLES_DIR / 'customer_rfm_segments.csv', index=False)

    retention_matrix = compute_cohort_retention(analytical_df)
    retention_matrix.to_csv(TABLES_DIR / 'cohort_retention_matrix.csv')

    transit_impact = analyze_transit_vs_repeat_purchasing(analytical_df)
    transit_impact.to_csv(TABLES_DIR / 'transit_repeat_impact.csv', index=False)

    # 6. Statistical Analysis
    print("[Step 6] Running descriptive statistics, correlation, ANOVA, and Chi-Square tests...")
    desc_stats = compute_descriptive_statistics(analytical_df)
    desc_stats.to_csv(TABLES_DIR / 'descriptive_statistics.csv', index=False)

    corr_results = compute_correlation_analysis(analytical_df)
    corr_results['spearman_matrix'].to_csv(TABLES_DIR / 'spearman_correlation_matrix.csv')
    corr_results['pearson_matrix'].to_csv(TABLES_DIR / 'pearson_correlation_matrix.csv')

    inferential_results = perform_inferential_tests(analytical_df)
    with open(REPORTS_DIR / 'inferential_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(inferential_results, f, indent=2)

    # 7. Executive Insights & Recommendations
    print("[Step 7] Generating data-driven insights and commercial recommendations...")
    insights = generate_executive_insights(kpis, regional_df, cat_df, brand_df, pareto_brand, pareto_cat)
    recommendations = generate_business_recommendations(kpis, regional_df, cat_df, brand_df)
    
    with open(REPORTS_DIR / 'executive_insights.json', 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2)
    with open(REPORTS_DIR / 'business_recommendations.json', 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2)

    # 8. Render and Export Visualizations
    print("[Step 8] Exporting interactive Plotly figures (HTML)...")
    fig_monthly = plot_monthly_revenue_trend(monthly_trends)
    fig_reg_bar = plot_regional_revenue_bar(regional_df)
    fig_reg_donut = plot_regional_revenue_donut(regional_df)
    fig_pareto_brand = plot_pareto_curve(pareto_brand, "Brand")
    fig_pareto_cat = plot_pareto_curve(pareto_cat, "Category")
    fig_cat_matrix = plot_category_revenue_margin(cat_df)
    fig_brand_matrix = plot_brand_risk_matrix(brand_df)
    fig_reg_matrix = plot_regional_opportunity_matrix(regional_df)
    fig_transit = plot_transit_vs_repeat(transit_impact)
    fig_rfm = plot_rfm_segments(rfm_summary)
    fig_cohort = plot_cohort_retention(retention_matrix)

    figs = {
        'monthly_revenue_trend.html': fig_monthly,
        'regional_revenue_bar.html': fig_reg_bar,
        'regional_revenue_donut.html': fig_reg_donut,
        'pareto_brand_analysis.html': fig_pareto_brand,
        'pareto_category_analysis.html': fig_pareto_cat,
        'category_economics_matrix.html': fig_cat_matrix,
        'brand_risk_matrix.html': fig_brand_matrix,
        'regional_opportunity_matrix.html': fig_reg_matrix,
        'transit_repeat_impact.html': fig_transit,
        'rfm_segmentation.html': fig_rfm,
        'cohort_retention_matrix.html': fig_cohort
    }

    for fname, fig in figs.items():
        fig.write_html(str(FIGURES_DIR / fname))

    print(f"  Successfully exported {len(figs)} interactive figures to {FIGURES_DIR}")
    print("=" * 70)
    print("PIPELINE EXECUTION COMPLETE & ALL TABLES/REPORTS POPULATED.")
    print("=" * 70)

if __name__ == '__main__':
    run_pipeline()
