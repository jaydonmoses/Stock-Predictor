import os
import sqlite3
import pandas as pd
from pathlib import Path

def get_db_path(db_name='stocks.db'):
    """Get the appropriate database path for the environment."""
    # In Vercel, use /tmp for temporary storage
    if os.environ.get('VERCEL'):
        tmp_path = f'/tmp/{db_name}'
        return tmp_path
    else:
        # Local development
        return db_name

def ensure_database_exists():
    """Ensure the database exists and is populated with data."""
    db_path = get_db_path()
    
    # Check if database exists
    if not os.path.exists(db_path):
        # Copy or recreate database
        create_database_from_csv(db_path)
    
    return db_path

def create_database_from_csv(db_path):
    """Create database from CSV files."""
    conn = sqlite3.connect(db_path)
    
    # Check if static files exist
    companies_csv = 'static/companies.csv'
    stock_data_csv = 'static/stock_data.csv'
    
    if os.path.exists(companies_csv) and os.path.exists(stock_data_csv):
        # Read CSV files into pandas DataFrames
        companies_df = pd.read_csv(companies_csv)
        stock_data_df = pd.read_csv(stock_data_csv)
        
        # Write DataFrames to SQLite
        companies_df.to_sql('companies', conn, if_exists='replace', index=False)
        stock_data_df.to_sql('stock_prices', conn, if_exists='replace', index=False)
    else:
        # Fallback: create minimal database with sample data
        create_sample_database(conn)
    
    conn.close()

def create_sample_database(conn):
    """Create a minimal database with sample data for when CSV files are not available."""
    cursor = conn.cursor()
    
    # Create companies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            ticker TEXT PRIMARY KEY,
            company_name TEXT,
            industry TEXT,
            sector TEXT,
            market_cap REAL
        )
    ''')
    
    # Create stock_prices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            ticker TEXT,
            date TEXT,
            price REAL,
            volume INTEGER
        )
    ''')
    
    # Insert sample companies
    sample_companies = [
        ('AAPL', 'Apple Inc.', 'Technology', 'Technology', 3000000000000),
        ('MSFT', 'Microsoft Corporation', 'Technology', 'Technology', 2800000000000),
        ('GOOGL', 'Alphabet Inc.', 'Technology', 'Communication Services', 1700000000000),
        ('AMZN', 'Amazon.com Inc.', 'E-commerce', 'Consumer Discretionary', 1500000000000),
        ('TSLA', 'Tesla Inc.', 'Automotive', 'Consumer Discretionary', 800000000000),
        ('META', 'Meta Platforms Inc.', 'Social Media', 'Communication Services', 750000000000),
        ('NVDA', 'NVIDIA Corporation', 'Semiconductors', 'Technology', 1100000000000),
        ('NFLX', 'Netflix Inc.', 'Streaming', 'Communication Services', 180000000000),
        ('AMD', 'Advanced Micro Devices', 'Semiconductors', 'Technology', 240000000000),
        ('INTC', 'Intel Corporation', 'Semiconductors', 'Technology', 200000000000)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO companies (ticker, company_name, industry, sector, market_cap)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_companies)
    
    # Insert sample stock prices (last 30 days for each stock)
    import datetime
    from random import uniform
    
    base_prices = {
        'AAPL': 180, 'MSFT': 380, 'GOOGL': 140, 'AMZN': 145, 'TSLA': 250,
        'META': 320, 'NVDA': 480, 'NFLX': 450, 'AMD': 140, 'INTC': 50
    }
    
    for ticker, base_price in base_prices.items():
        for i in range(30):
            date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            # Add some random variation
            price = base_price * uniform(0.95, 1.05)
            volume = int(uniform(1000000, 10000000))
            
            cursor.execute('''
                INSERT OR REPLACE INTO stock_prices (ticker, date, price, volume)
                VALUES (?, ?, ?, ?)
            ''', (ticker, date, price, volume))
    
    conn.commit()

def get_portfolio_db_path():
    """Get the portfolio database path."""
    return get_db_path('portfolio.db')