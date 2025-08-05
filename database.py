import sqlite3
import pandas as pd
import os

def init_db():
    """Initialize SQLite database and create tables from CSV files."""
    # Create database connection
    conn = sqlite3.connect('stocks.db')
    
    # Read CSV files into pandas DataFrames
    companies_df = pd.read_csv('static/companies.csv')
    stock_data_df = pd.read_csv('static/stock_data.csv')
    
    # Write DataFrames to SQLite
    companies_df.to_sql('companies', conn, if_exists='replace', index=False)
    stock_data_df.to_sql('stock_prices', conn, if_exists='replace', index=False)
    
    conn.close()

def get_stock_data(ticker):
    """Get stock price data for a specific ticker."""
    conn = sqlite3.connect('stocks.db')
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
    conn = sqlite3.connect('stocks.db')
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
    conn = sqlite3.connect('stocks.db')
    query = """
    SELECT ticker, company_name, market_cap
    FROM companies
    ORDER BY market_cap DESC
    LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.to_dict('records')