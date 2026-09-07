"""
Statistical Analysis Module.
Conducts rigorous descriptive, inferential, and correlation analyses.
Reports p-values, effect sizes, ANOVA, Kruskal-Wallis, and Chi-Square tests.
Strictly separates observed statistical association from causal inference.
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any

def compute_descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Computes comprehensive distributional metrics for primary financial variables."""
    numeric_cols = ['gross_revenue', 'net_revenue', 'discount_amount', 'margin', 'unit_price', 'quantity', 'transit_days']
    valid_cols = [c for c in numeric_cols if c in df.columns]

    stats_list = []
    for col in valid_cols:
        series = df[col].dropna()
        q25 = float(series.quantile(0.25))
        q75 = float(series.quantile(0.75))
        stats_list.append({
            'variable': col,
            'count': int(len(series)),
            'mean': round(float(series.mean()), 2),
            'std_dev': round(float(series.std()), 2),
            'variance': round(float(series.var()), 2),
            'median': round(float(series.median()), 2),
            'iqr': round(float(q75 - q25), 2),
            'min': round(float(series.min()), 2),
            'p25': round(q25, 2),
            'p75': round(q75, 2),
            'max': round(float(series.max()), 2),
            'skewness': round(float(series.skew()), 2)
        })

    return pd.DataFrame(stats_list)

def compute_correlation_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes Pearson and Spearman correlation matrices with associated p-values."""
    cols = ['unit_price', 'quantity', 'discount_rate', 'net_revenue', 'margin_rate', 'transit_days', 'return_flag', 'dispute_flag']
    cols = [c for c in cols if c in df.columns]

    df_clean = df[cols].dropna()

    pearson_corr = df_clean.corr(method='pearson').round(4)
    spearman_corr = df_clean.corr(method='spearman').round(4)

    # Compute p-values matrix for Spearman
    n = len(cols)
    p_values = pd.DataFrame(np.zeros((n, n)), index=cols, columns=cols)
    for i in range(n):
        for j in range(n):
            if i == j:
                p_values.iloc[i, j] = 1.0
            else:
                _, p = stats.spearmanr(df_clean[cols[i]], df_clean[cols[j]])
                p_values.iloc[i, j] = round(float(p), 5)

    return {
        'pearson_matrix': pearson_corr,
        'spearman_matrix': spearman_corr,
        'p_values_matrix': p_values
    }

def perform_inferential_tests(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Executes ANOVA / Kruskal-Wallis across regions and Chi-Square tests
    for categorical associations (transit delays vs return/dispute).
    """
    results = {}

    # 1. Kruskal-Wallis test: Does AOV vary significantly across Regions?
    reg_groups = [group['net_revenue'].values for _, group in df.groupby('region')]
    kw_stat, kw_p = stats.kruskal(*reg_groups)
    results['kruskal_wallis_region_revenue'] = {
        'test_name': 'Kruskal-Wallis H-Test (Net Revenue by Region)',
        'statistic': round(float(kw_stat), 4),
        'p_value': float(kw_p),
        'significant_at_05': bool(kw_p < 0.05),
        'interpretation': 'Statistically significant differences observed across regional revenues.' if kw_p < 0.05 else 'No statistically significant differences detected across regions.'
    }

    # 2. ANOVA: Does Margin Rate vary significantly across Categories?
    cat_groups = [group['margin_rate'].dropna().values for _, group in df.groupby('category')]
    anova_stat, anova_p = stats.f_oneway(*cat_groups)
    results['anova_category_margin'] = {
        'test_name': 'One-Way ANOVA (Margin Rate by Category)',
        'statistic': round(float(anova_stat), 4),
        'p_value': float(anova_p),
        'significant_at_05': bool(anova_p < 0.05),
        'interpretation': 'Product categories have statistically distinct margin profiles.' if anova_p < 0.05 else 'Categories exhibit homogenous margin profiles.'
    }

    # 3. Chi-Square Test: Association between Transit Delay Bucket and Return Flag
    contingency = pd.crosstab(df['transit_bucket'], df['return_flag'])
    chi2, chi_p, dof, _ = stats.chi2_contingency(contingency)
    # Cramer's V effect size
    n = contingency.sum().sum()
    min_dim = min(contingency.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0.0

    results['chi_square_transit_return'] = {
        'test_name': 'Chi-Square Test of Independence (Transit Delay vs Return Rate)',
        'chi2_statistic': round(float(chi2), 4),
        'p_value': float(chi_p),
        'degrees_of_freedom': int(dof),
        'cramers_v_effect_size': round(float(cramers_v), 4),
        'significant_at_05': bool(chi_p < 0.05),
        'caveat': 'Observational association only. Does not imply transit delay is the sole causal driver of returns.'
    }

    return results
