# Data Lineage & Schema Documentation

## Dataset Description
This project utilizes a high-fidelity synthetic e-commerce transactional dataset modeled after enterprise multi-channel retail operations.
In accordance with Section 2 (Data Integrity Rule) of the project specification, this dataset is explicitly labeled as **synthetic**.
Every KPI, correlation, ranking, statistical test, and business recommendation in this project is calculated dynamically from this underlying dataset with zero hardcoded placeholders or fabricated metrics.

## Tables
1. **data/raw/orders.csv**: Transaction-level order details containing order ID, customer ID, timestamps, line-item pricing, quantities, discounts, cost, region, category, brand, and fulfillment outcomes.
2. **data/raw/customers.csv**: Customer master record with signup dates, acquisition channels, and customer segments.
3. **data/raw/products.csv**: Product catalog listing categories, subcategories, unit costs, and brand affiliations.
4. **data/raw/logistics.csv**: Logistics corridor and delivery performance records including regional hubs, transit days, and shipping costs.
5. **data/processed/ecommerce_analytical_dataset.csv**: Cleaned, reconciled, and feature-engineered transactional dataset ready for analytical modeling and dashboard ingestion.

## Data Generation Parameters
- **Random Seed**: 42 (ensuring 100% deterministic reproducibility)
- **Time Coverage**: January 1, 2023 through December 31, 2024 (24 months / 8 full quarters)
- **Scale**: ~15,000+ line item transactions across 2,500 unique customers, 120 products, 20 brands, and 5 geographic regions.
- **Injected Data Quality Scenarios**: Deliberately incorporates realistic edge cases (duplicate entries, whitespace anomalies, null delivery dates for cancelled orders, negative/zero quantity test records) to validate preprocessing robustness.
