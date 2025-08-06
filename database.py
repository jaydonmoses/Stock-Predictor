import sqlite3
import pandas as pd
import os
from database_config import ensure_database_exists, get_db_path

def init_db():
    """Initialize SQLite database and create tables from CSV files."""
    # Ensure database exists and return path
    db_path = ensure_database_exists()
    return db_path

def get_stock_data(ticker):
    """Get stock price data for a specific ticker."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT date, price, volume
    FROM stock_prices
    WHERE ticker = ?
    ORDER BY date DESC
    LIMIT 100
    """
    df = pd.read_sql_query(query, conn, params=(ticker,))
    conn.close()
    return df

def get_company_info(ticker):
    """Get company information for a specific ticker."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    query = """
    SELECT ticker, company_name, industry, sector
    FROM companies
    WHERE ticker = ?
    """
    df = pd.read_sql_query(query, conn, params=(ticker,))
    conn.close()
    return df.to_dict('records')[0] if not df.empty else None

def popular_companies():
    """Get a list of popular companies based on market cap."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    query = """
    SELECT ticker, company_name, market_cap
    FROM companies
    ORDER BY market_cap DESC
    LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.to_dict('records')