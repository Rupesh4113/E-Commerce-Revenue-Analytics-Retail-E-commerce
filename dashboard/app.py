"""
Interactive Executive Revenue Analytics Dashboard.
Built with Streamlit and Plotly for senior leadership commercial decision-support.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
import sys

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.data_loader import load_processed_data
from src.revenue_analysis import compute_executive_kpis, compute_temporal_trends, compute_pareto_analysis
from src.regional_analysis import compute_regional_performance
from src.category_analysis import compute_category_performance, compute_market_basket_bundling
from src.brand_analysis import compute_brand_performance
from src.customer_analysis import compute_rfm_segmentation, compute_cohort_retention, analyze_transit_vs_repeat_purchasing
from src.insights import generate_executive_insights, generate_business_recommendations
from src.visualization import (
    plot_monthly_revenue_trend, plot_regional_revenue_bar, plot_regional_revenue_donut,
    plot_pareto_curve, plot_category_revenue_margin, plot_brand_risk_matrix,
    plot_regional_opportunity_matrix, plot_transit_vs_repeat, plot_rfm_segments, plot_cohort_retention
)

# Page Setup
st.set_page_config(
    page_title="E-Commerce Revenue Analytics | Executive Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main {background-color: #F9FAFB;}
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {font-size: 26px; font-weight: 700; color: #1E3A8A;}
    .metric-label {font-size: 13px; color: #6B7280; text-transform: uppercase; font-weight: 600;}
    .insight-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 4px;
    }
    .rec-box {
        background-color: #ECFDF5;
        border-left: 4px solid #10B981;
        padding: 14px;
        margin-bottom: 12px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Cache Data Ingestion
@st.cache_data
def get_data():
    return load_processed_data()

try:
    df_raw = get_data()
except Exception as e:
    st.error(f"Error loading analytical dataset: {e}. Please run `python run_pipeline.py` first.")
    st.stop()

# Sidebar Filters
st.sidebar.title("🎛️ Analytics Controls")
st.sidebar.markdown("---")

min_date = df_raw['order_date'].min().date()
max_date = df_raw['order_date'].max().date()

date_range = st.sidebar.date_input(
    "Select Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

all_regions = sorted(df_raw['region'].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Filter by Region", options=all_regions, default=all_regions)

all_categories = sorted(df_raw['category'].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect("Filter by Category", options=all_categories, default=all_categories)

if 'customer_segment' in df_raw.columns:
    all_segments = sorted(df_raw['customer_segment'].dropna().unique().tolist())
    selected_segments = st.sidebar.multiselect("Customer Segment", options=all_segments, default=all_segments)
else:
    selected_segments = []

# Apply Filter Logic
df_filtered = df_raw.copy()
if len(date_range) == 2:
    start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_filtered = df_filtered[(df_filtered['order_date'] >= start_dt) & (df_filtered['order_date'] <= end_dt)]

if selected_regions:
    df_filtered = df_filtered[df_filtered['region'].isin(selected_regions)]

if selected_categories:
    df_filtered = df_filtered[df_filtered['category'].isin(selected_categories)]

if selected_segments and 'customer_segment' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['customer_segment'].isin(selected_segments)]

if df_filtered.empty:
    st.warning("⚠️ No transactional records match your selected filter criteria. Please broaden your filters.")
    st.stop()

# Header
st.title("📊 E-Commerce Revenue Analytics & Decision-Support System")
st.markdown("*Enterprise commercial intelligence covering revenue concentration, margin drivers, logistics efficiency, and growth levers.*")
st.markdown("---")

# Compute Dynamic KPIs on Filtered View
kpis = compute_executive_kpis(df_filtered)

# Navigation Tabs
tabs = st.tabs([
    "📈 Executive Overview",
    "🗺️ Regional Performance",
    "📦 Product & Category",
    "🏷️ Brand Portfolio",
    "👥 Customer Analytics",
    "🚚 Logistics & Operations",
    "💡 Strategic Insights & Actions"
])

# TAB 1: EXECUTIVE OVERVIEW
with tabs[0]:
    st.subheader("Commercial Executive Scorecard")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Net Revenue</div><div class="metric-value">${kpis["total_net_revenue"]:,.2f}</div><small>Gross: ${kpis["total_gross_revenue"]:,.2f}</small></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Gross Margin %</div><div class="metric-value">{kpis["gross_margin_pct"]*100:.1f}%</div><small>Contribution: ${kpis["margin_contribution"]:,.2f}</small></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Orders & AOV</div><div class="metric-value">{kpis["total_orders"]:,}</div><small>AOV: ${kpis["aov"]:.2f}</small></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">YoY Growth / Repeat Rate</div><div class="metric-value">+{kpis["revenue_growth_yoy"]*100:.1f}%</div><small>Repeat Customers: {kpis["repeat_purchase_rate"]*100:.1f}%</small></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    row2_1, row2_2 = st.columns([3, 2])
    with row2_1:
        monthly_trends = compute_temporal_trends(df_filtered)
        st.plotly_chart(plot_monthly_revenue_trend(monthly_trends), use_container_width=True)
    with row2_2:
        reg_summary = compute_regional_performance(df_filtered)
        st.plotly_chart(plot_regional_revenue_donut(reg_summary), use_container_width=True)

    st.markdown("### Revenue Concentration (Pareto Analysis)")
    pareto_choice = st.radio("Select Pareto Dimension:", options=["Brand", "Category", "Region"], horizontal=True)
    pareto_col = pareto_choice.lower()
    pareto_res = compute_pareto_analysis(df_filtered, group_col=pareto_col)
    
    col_p1, col_p2 = st.columns([3, 2])
    with col_p1:
        st.plotly_chart(plot_pareto_curve(pareto_res, pareto_choice), use_container_width=True)
    with col_p2:
        st.markdown(f"**Concentration Benchmarks ({pareto_choice}):**")
        st.markdown(f"- **Top 1 Share:** `{pareto_res['top_shares']['top_1_share']*100:.1f}%`")
        st.markdown(f"- **Top 3 Share:** `{pareto_res['top_shares']['top_3_share']*100:.1f}%`")
        st.markdown(f"- **Top 5 Share:** `{pareto_res['top_shares']['top_5_share']*100:.1f}%`")
        st.markdown(f"- **Entities needed for 50% Revenue:** `{pareto_res['threshold_counts'].get('50%', 'N/A')}`")
        st.markdown(f"- **Entities needed for 80% Revenue:** `{pareto_res['threshold_counts'].get('80%', 'N/A')}`")
        st.dataframe(pareto_res['table'].head(8), use_container_width=True)

# TAB 2: REGIONAL PERFORMANCE
with tabs[1]:
    st.subheader("Geographic Demand & Regional Growth Opportunities")
    reg_df = compute_regional_performance(df_filtered)
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.plotly_chart(plot_regional_revenue_bar(reg_df), use_container_width=True)
    with r_col2:
        st.plotly_chart(plot_regional_opportunity_matrix(reg_df), use_container_width=True)

    st.markdown("### Regional Commercial & Logistics Corridor Breakdown")
    st.dataframe(
        reg_df[['region', 'net_revenue', 'revenue_share', 'growth_rate', 'gross_margin_pct', 'aov', 'orders', 'customers', 'return_rate', 'avg_transit_days', 'opportunity_classification']]
        .style.format({
            'net_revenue': '${:,.2f}',
            'revenue_share': '{:.1%}',
            'growth_rate': '{:.1%}',
            'gross_margin_pct': '{:.1%}',
            'aov': '${:.2f}',
            'orders': '{:,}',
            'customers': '{:,}',
            'return_rate': '{:.1%}',
            'avg_transit_days': '{:.1f} days'
        }),
        use_container_width=True
    )

# TAB 3: PRODUCT & CATEGORY
with tabs[2]:
    st.subheader("Category Unit Economics & Profitability Drivers")
    cat_df = compute_category_performance(df_filtered)

    c_col1, c_col2 = st.columns([3, 2])
    with c_col1:
        st.plotly_chart(plot_category_revenue_margin(cat_df), use_container_width=True)
    with c_col2:
        st.markdown("### Category Classifications")
        for _, row in cat_df.iterrows():
            st.markdown(f"- **{row['category']}**: `{row['classification']}` (Margin: {row['gross_margin_pct']*100:.1f}%, Rev: ${row['net_revenue']:,.2f})")

    st.markdown("### Product Bundling Recommendations (Market Basket Affinity)")
    bundling_df = compute_market_basket_bundling(df_filtered)
    st.dataframe(
        bundling_df[['bundle_candidate', 'co_occurrence_count', 'support_rate', 'recommended_strategy']]
        .style.format({'support_rate': '{:.2%}'}),
        use_container_width=True
    )

# TAB 4: BRAND PORTFOLIO
with tabs[3]:
    st.subheader("Brand Concentration & Risk Analysis")
    brand_df = compute_brand_performance(df_filtered)
    
    b_col1, b_col2 = st.columns([3, 2])
    with b_col1:
        st.plotly_chart(plot_brand_risk_matrix(brand_df), use_container_width=True)
    with b_col2:
        st.markdown("### Brand Concentration Metrics")
        st.markdown(f"- **Top 1 Brand Share:** `{brand_df.iloc[0]['revenue_share']*100:.1f}%` ({brand_df.iloc[0]['brand']})")
        st.markdown(f"- **Top 3 Brand Share:** `{brand_df.iloc[:3]['revenue_share'].sum()*100:.1f}%`")
        st.markdown(f"- **Top 5 Brand Share:** `{brand_df.iloc[:5]['revenue_share'].sum()*100:.1f}%`")
        st.markdown("---")
        st.markdown("**Anchor Brands (High Vol & Reach):**")
        anchors = brand_df[brand_df['portfolio_classification'] == 'Anchor Brand']['brand'].tolist()
        st.write(", ".join(anchors) if anchors else "None")
        st.markdown("**Risk Brands (High Rev / Low Margin or High Return):**")
        risks = brand_df[brand_df['portfolio_classification'] == 'Risk Brand']['brand'].tolist()
        st.write(", ".join(risks) if risks else "None")

    st.dataframe(
        brand_df[['brand', 'category', 'net_revenue', 'revenue_share', 'gross_margin_pct', 'units', 'aov', 'growth_rate', 'return_rate', 'portfolio_classification']]
        .style.format({
            'net_revenue': '${:,.2f}',
            'revenue_share': '{:.1%}',
            'gross_margin_pct': '{:.1%}',
            'units': '{:,}',
            'aov': '${:.2f}',
            'growth_rate': '{:.1%}',
            'return_rate': '{:.1%}'
        }),
        use_container_width=True
    )

# TAB 5: CUSTOMER ANALYTICS
with tabs[4]:
    st.subheader("Customer Intelligence & Lifecycle Segmentation")
    rfm_df, rfm_summary = compute_rfm_segmentation(df_filtered)
    retention_matrix = compute_cohort_retention(df_filtered)
    
    cust_c1, cust_c2 = st.columns(2)
    with cust_c1:
        st.plotly_chart(plot_rfm_segments(rfm_summary), use_container_width=True)
    with cust_c2:
        st.plotly_chart(plot_cohort_retention(retention_matrix), use_container_width=True)

    st.markdown("### RFM Segment Revenue Contribution Table")
    st.dataframe(
        pd.DataFrame(rfm_summary).style.format({
            'total_revenue': '${:,.2f}',
            'revenue_share': '{:.1%}',
            'avg_monetary': '${:,.2f}',
            'avg_recency': '{:.0f} days',
            'avg_frequency': '{:.1f} orders',
            'customer_count': '{:,}'
        }),
        use_container_width=True
    )

# TAB 6: LOGISTICS & OPERATIONS
with tabs[5]:
    st.subheader("Fulfillment Efficiency & Customer Outcomes")
    transit_df = analyze_transit_vs_repeat_purchasing(df_filtered)
    
    l_col1, l_col2 = st.columns(2)
    with l_col1:
        st.plotly_chart(plot_transit_vs_repeat(transit_df), use_container_width=True)
    with l_col2:
        fig_transit_hist = px.histogram(
            df_filtered,
            x='transit_days',
            color='region',
            title='<b>Transit Days Distribution by Region</b>',
            labels={'transit_days': 'Transit Days'},
            template='plotly_white'
        )
        st.plotly_chart(fig_transit_hist, use_container_width=True)

    st.info("⚠️ **Analytical Integrity Standard**: Observational association only. Correlation does not imply transit time is the sole causal driver of returns or repeat orders.")

# TAB 7: STRATEGIC INSIGHTS & ACTIONS
with tabs[6]:
    st.subheader("Executive Insights (Metric ➔ Evidence ➔ Interpretation ➔ Action)")
    insights = generate_executive_insights(kpis, reg_df, cat_df, brand_df, pareto_res, pareto_res)
    for ins in insights:
        st.markdown(f"""
        <div class="insight-box">
            <h4>📌 {ins['theme']}</h4>
            <p><b>Key Metric:</b> {ins['metric']}</p>
            <p><b>Observed Evidence:</b> {ins['evidence']}</p>
            <p><b>Commercial Interpretation:</b> {ins['interpretation']}</p>
            <p><b>Recommended Action:</b> {ins['action']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Prioritized Business Recommendations")
    recommendations = generate_business_recommendations(kpis, reg_df, cat_df, brand_df)
    for rec in recommendations:
        st.markdown(f"""
        <div class="rec-box">
            <h4>🎯 {rec['domain']} — Priority: [{rec['priority']}]</h4>
            <p><b>Recommendation:</b> {rec['recommendation']}</p>
            <p><b>Supporting Data:</b> {rec['evidence']}</p>
            <p><b>Expected Commercial Impact:</b> {rec['expected_kpi_impact']}</p>
            <p><b>Implementation Risk:</b> {rec['risk_or_limitation']}</p>
        </div>
        """, unsafe_allow_html=True)
