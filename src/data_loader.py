"""
Data Ingestion and Query Helper Module.
Supports loading raw/processed data and executing SQL queries via DuckDB.
"""
import pandas as pd
import duckdb
from pathlib import Path
from typing import Optional
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def load_raw_orders(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (RAW_DATA_DIR / 'orders.csv')
    return pd.read_csv(path)

def load_raw_customers(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (RAW_DATA_DIR / 'customers.csv')
    return pd.read_csv(path)

def load_raw_products(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (RAW_DATA_DIR / 'products.csv')
    return pd.read_csv(path)

def load_raw_logistics(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (RAW_DATA_DIR / 'logistics.csv')
    return pd.read_csv(path)

def load_processed_data(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (PROCESSED_DATA_DIR / 'ecommerce_analytical_dataset.csv')
    return pd.read_csv(path, parse_dates=['order_date', 'shipping_date', 'delivery_date'])

def execute_sql_query(query: str, dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Execute arbitrary SQL queries against provided DataFrames in DuckDB."""
    con = duckdb.connect(database=':memory:')
    for name, df in dfs.items():
        con.register(name, df)
    result = con.execute(query).df()
    con.close()
    return result
