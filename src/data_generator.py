"""
Synthetic E-Commerce Data Generator.
Produces high-fidelity, relational transactional e-commerce dataset for revenue analytics.
Explicitly labeled as synthetic per project requirements.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import RAW_DATA_DIR, RANDOM_SEED

def generate_dataset(n_orders=16000, seed=RANDOM_SEED):
    np.random.seed(seed)
    random.seed(seed)

    print(f"Generating synthetic e-commerce dataset (seed={seed}, target_orders={n_orders})...")

    # 1. Customer Master Table
    n_customers = 2800
    customer_ids = [f"CUST-{i:04d}" for i in range(1, n_customers + 1)]
    segments = ['Consumer', 'Small Business', 'Corporate']
    seg_weights = [0.65, 0.23, 0.12]
    channels = ['Organic Search', 'Paid Ads', 'Social Media', 'Email Campaign', 'Referral']
    chan_weights = [0.35, 0.28, 0.17, 0.12, 0.08]

    start_signup = datetime(2022, 1, 1)
    end_signup = datetime(2024, 6, 30)
    signup_days_range = (end_signup - start_signup).days

    cust_signup_dates = [start_signup + timedelta(days=int(np.random.randint(0, signup_days_range))) for _ in range(n_customers)]
    cust_segments = np.random.choice(segments, size=n_customers, p=seg_weights)
    cust_channels = np.random.choice(channels, size=n_customers, p=chan_weights)

    customers_df = pd.DataFrame({
        'customer_id': customer_ids,
        'customer_segment': cust_segments,
        'acquisition_channel': cust_channels,
        'signup_date': [d.strftime('%Y-%m-%d') for d in cust_signup_dates]
    })

    # 2. Product Catalog & Brand Master Table
    categories_spec = {
        'Electronics': {
            'subcategories': ['Smartphones', 'Laptops', 'Audio & Headphones', 'Accessories'],
            'price_range': (25.0, 950.0),
            'margin_range': (0.18, 0.42),
            'brands': ['TechNova', 'OmniVolt', 'PulseAudio', 'SoundPeak']
        },
        'Apparel & Fashion': {
            'subcategories': ["Men's Apparel", "Women's Apparel", "Footwear", "Bags & Luggage"],
            'price_range': (18.0, 240.0),
            'margin_range': (0.40, 0.65),
            'brands': ['UrbanChic', 'SwiftStyle', 'ApexGear', 'VogueEra']
        },
        'Home & Kitchen': {
            'subcategories': ['Cookware', 'Furniture & Decor', 'Bedding', 'Small Appliances'],
            'price_range': (22.0, 480.0),
            'margin_range': (0.32, 0.55),
            'brands': ['AuraHome', 'LuxLiving', 'HavenCraft', 'CozyNest']
        },
        'Health & Beauty': {
            'subcategories': ['Skincare', 'Haircare', 'Fragrance', 'Wellness & Vitamins'],
            'price_range': (14.0, 160.0),
            'margin_range': (0.45, 0.72),
            'brands': ['GlowLabs', 'PureEssence', 'DermaCare', 'VitalBotanics']
        },
        'Sports & Outdoors': {
            'subcategories': ['Fitness Equipment', 'Outdoor Gear', 'Sportswear', 'Cycling & Action'],
            'price_range': (20.0, 420.0),
            'margin_range': (0.28, 0.52),
            'brands': ['ZenFit', 'TrailBlaze', 'SummitPro', 'VeloSprint']
        }
    }

    products = []
    prod_id_counter = 1
    for cat, spec in categories_spec.items():
        for brand in spec['brands']:
            for subcat in spec['subcategories']:
                n_items = np.random.randint(1, 3)
                for item_idx in range(n_items):
                    p_id = f"PROD-{prod_id_counter:04d}"
                    base_price = round(float(np.random.uniform(*spec['price_range'])), 2)
                    margin_pct = float(np.random.uniform(*spec['margin_range']))
                    if brand in ['LuxLiving', 'PureEssence']:
                        margin_pct = max(margin_pct, 0.52)  # High Margin Brand
                    elif brand in ['OmniVolt', 'SwiftStyle']:
                        margin_pct = min(margin_pct, 0.22)  # Risk Brand (low margin)
                    
                    cost = round(base_price * (1.0 - margin_pct), 2)
                    p_name = f"{brand} {subcat} {item_idx + 1}"
                    products.append({
                        'product_id': p_id,
                        'product_name': p_name,
                        'category': cat,
                        'subcategory': subcat,
                        'brand': brand,
                        'unit_price': base_price,
                        'product_cost': cost
                    })
                    prod_id_counter += 1

    products_df = pd.DataFrame(products)

    # 3. Geography & Regional Hubs
    regional_data = {
        'North': {
            'hub': 'Hub-North-Chicago',
            'states': ['Illinois', 'Michigan', 'Ohio', 'Wisconsin'],
            'cities': ['Chicago', 'Detroit', 'Columbus', 'Milwaukee'],
            'base_weight': 0.32,
            'base_transit': 3.2
        },
        'West': {
            'hub': 'Hub-West-Seattle',
            'states': ['Washington', 'California', 'Oregon', 'Nevada'],
            'cities': ['Seattle', 'San Francisco', 'Portland', 'Las Vegas'],
            'base_weight': 0.28,
            'base_transit': 3.6
        },
        'East': {
            'hub': 'Hub-East-NewYork',
            'states': ['New York', 'Pennsylvania', 'Massachusetts', 'New Jersey'],
            'cities': ['New York', 'Philadelphia', 'Boston', 'Newark'],
            'base_weight': 0.22,
            'base_transit': 3.0
        },
        'South': {
            'hub': 'Hub-South-Atlanta',
            'states': ['Georgia', 'Florida', 'North Carolina', 'Texas'],
            'cities': ['Atlanta', 'Miami', 'Charlotte', 'Dallas'],
            'base_weight': 0.12,
            'base_transit': 4.1
        },
        'Central': {
            'hub': 'Hub-Central-Denver',
            'states': ['Colorado', 'Missouri', 'Kansas', 'Utah'],
            'cities': ['Denver', 'St. Louis', 'Kansas City', 'Salt Lake City'],
            'base_weight': 0.06,
            'base_transit': 4.5
        }
    }

    # 4. Orders Generation
    order_start = datetime(2023, 1, 1)
    order_end = datetime(2024, 12, 31)
    total_days = (order_end - order_start).days

    regions = list(regional_data.keys())
    reg_probs = [regional_data[r]['base_weight'] for r in regions]

    core_customers = customer_ids[:1000]
    casual_customers = customer_ids[1000:]

    orders = []
    order_id_counter = 10001

    for i in range(n_orders):
        # Seasonality distribution (heavier in 2024 and Q4)
        day_offset = int(np.random.triangular(0, total_days * 0.65, total_days))
        ord_date = order_start + timedelta(days=day_offset)
        
        # Customer selection
        if np.random.rand() < 0.62:
            c_id = np.random.choice(core_customers)
        else:
            c_id = np.random.choice(casual_customers)

        # Brand weighting for concentration
        prod_weights = []
        for b in products_df['brand']:
            if b in ['TechNova', 'AuraHome', 'ApexGear']:
                prod_weights.append(3.5)
            elif b in ['ZenFit', 'PulseAudio', 'GlowLabs', 'UrbanChic']:
                prod_weights.append(2.0)
            else:
                prod_weights.append(1.0)
        
        prod_row = products_df.sample(1, weights=prod_weights).iloc[0]

        p_id = prod_row['product_id']
        u_price = float(prod_row['unit_price'])
        u_cost = float(prod_row['product_cost'])

        qty = int(np.random.choice([1, 2, 3, 4, 5], p=[0.72, 0.18, 0.06, 0.03, 0.01]))
        gross_rev = round(qty * u_price, 2)

        disc_prob = 0.35
        if np.random.rand() < disc_prob:
            disc_rate = float(np.random.choice([0.05, 0.10, 0.15, 0.20, 0.25], p=[0.25, 0.35, 0.20, 0.15, 0.05]))
            disc_amt = round(gross_rev * disc_rate, 2)
        else:
            disc_amt = 0.0

        net_rev = round(gross_rev - disc_amt, 2)
        total_cost = round(qty * u_cost, 2)
        margin_amt = round(net_rev - total_cost, 2)

        reg = np.random.choice(regions, p=reg_probs)
        state = np.random.choice(regional_data[reg]['states'])
        city = np.random.choice(regional_data[reg]['cities'])
        hub = regional_data[reg]['hub']
        
        base_t = regional_data[reg]['base_transit']
        transit = int(max(1, round(np.random.gamma(shape=base_t * 2, scale=0.5))))
        shipping_cost = round(float(np.random.uniform(5.50, 18.50) + transit * 0.75), 2)

        ship_date = ord_date + timedelta(days=int(np.random.choice([1, 2])))
        deliv_date = ship_date + timedelta(days=transit)

        delay_factor = 1.0 + (0.15 if transit > 5 else 0.0)
        ret_prob = min(0.18, 0.045 * delay_factor * (1.35 if prod_row['category'] == 'Apparel & Fashion' else 1.0))
        disp_prob = min(0.08, 0.012 * delay_factor)

        is_returned = 1 if np.random.rand() < ret_prob else 0
        is_dispute = 1 if (is_returned and np.random.rand() < disp_prob * 3) or (np.random.rand() < disp_prob) else 0

        deliv_status = 'Delivered'
        if is_returned:
            deliv_status = 'Returned'
        elif np.random.rand() < 0.02:
            deliv_status = 'Cancelled'
            deliv_date = None

        ord_record = {
            'order_id': f"ORD-{order_id_counter}",
            'customer_id': c_id,
            'order_date': ord_date.strftime('%Y-%m-%d'),
            'product_id': p_id,
            'product_name': prod_row['product_name'],
            'quantity': qty,
            'unit_price': u_price,
            'gross_revenue': gross_rev,
            'discount_amount': disc_amt,
            'net_revenue': net_rev,
            'product_cost': total_cost,
            'margin': margin_amt,
            'region': reg,
            'state': state,
            'city': city,
            'category': prod_row['category'],
            'subcategory': prod_row['subcategory'],
            'brand': prod_row['brand'],
            'shipping_date': ship_date.strftime('%Y-%m-%d'),
            'delivery_date': deliv_date.strftime('%Y-%m-%d') if deliv_date else None,
            'delivery_status': deliv_status,
            'return_flag': is_returned,
            'dispute_flag': is_dispute,
            'logistics_hub': hub,
            'transit_days': transit if deliv_date else None,
            'shipping_cost': shipping_cost
        }
        orders.append(ord_record)
        order_id_counter += 1

    orders_df = pd.DataFrame(orders)

    # Inject controlled anomalies for data cleaning testing
    # 1. Duplicates (15 rows)
    dup_rows = orders_df.sample(15, random_state=seed)
    orders_df = pd.concat([orders_df, dup_rows], ignore_index=True)

    # 2. Non-positive quantities (12 rows)
    bad_qty_idx = np.random.choice(orders_df.index, size=12, replace=False)
    orders_df.loc[bad_qty_idx[:6], 'quantity'] = 0
    orders_df.loc[bad_qty_idx[6:], 'quantity'] = -1

    # 3. Whitespace and casing anomalies (25 rows)
    anomaly_idx = np.random.choice(orders_df.index, size=25, replace=False)
    for idx in anomaly_idx[:12]:
        val = orders_df.loc[idx, 'region']
        orders_df.loc[idx, 'region'] = f" {str(val).lower()} "
    for idx in anomaly_idx[12:]:
        val = orders_df.loc[idx, 'category']
        orders_df.loc[idx, 'category'] = str(val).upper()

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    orders_df.to_csv(RAW_DATA_DIR / 'orders.csv', index=False)
    customers_df.to_csv(RAW_DATA_DIR / 'customers.csv', index=False)
    products_df.to_csv(RAW_DATA_DIR / 'products.csv', index=False)
    
    corridors = []
    for reg, val in regional_data.items():
        corridors.append({
            'region': reg,
            'logistics_hub': val['hub'],
            'base_transit_days': val['base_transit'],
            'states_serviced': ', '.join(val['states'])
        })
    pd.DataFrame(corridors).to_csv(RAW_DATA_DIR / 'logistics.csv', index=False)

    print(f"Raw datasets successfully created in {RAW_DATA_DIR}:")
    print(f"  - orders.csv: {len(orders_df):,} records")
    print(f"  - customers.csv: {len(customers_df):,} records")
    print(f"  - products.csv: {len(products_df):,} records")
    print(f"  - logistics.csv: {len(corridors):,} records")
    return orders_df, customers_df, products_df

if __name__ == '__main__':
    generate_dataset()
