import sqlite3
import pandas as pd
import os

def init_db():
    """Initialize SQLite database and create tables from CSV files with memory optimization."""
    # Create database connection
    conn = sqlite3.connect('stocks.db')
    
    # Create portfolio simulation tables
    cursor = conn.cursor()
    
    # Portfolio table to track overall portfolio value
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total_value REAL NOT NULL,
            cash_balance REAL NOT NULL,
            total_stocks_value REAL NOT NULL,
            daily_return REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Trades table to track individual trades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            action TEXT NOT NULL,
            shares REAL NOT NULL,
            price REAL NOT NULL,
            total_amount REAL NOT NULL,
            prediction REAL,
            confidence REAL,
            trade_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Holdings table to track current stock positions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT UNIQUE NOT NULL,
            shares REAL NOT NULL,
            avg_price REAL NOT NULL,
            current_price REAL DEFAULT 0,
            current_value REAL DEFAULT 0,
            total_return REAL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initialize portfolio if it doesn't exist
    cursor.execute('SELECT COUNT(*) FROM portfolio')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO portfolio (date, total_value, cash_balance, total_stocks_value)
            VALUES (date('now'), 10000.0, 10000.0, 0.0)
        ''')
    
    conn.commit()
    
    # Read CSV files in chunks to reduce memory usage
    try:
        # Read companies CSV (usually smaller)
        companies_df = pd.read_csv('static/companies.csv')
        companies_df.to_sql('companies', conn, if_exists='replace', index=False)
        
        # Read stock data in chunks if it's large
        if os.path.exists('static/stock_data.csv'):
            chunk_size = 10000  # Process in smaller chunks
            for chunk in pd.read_csv('static/stock_data.csv', chunksize=chunk_size):
                chunk.to_sql('stock_prices', conn, if_exists='append', index=False)
    except FileNotFoundError as e:
        print(f"Warning: {e}. Database initialized without CSV data.")
    
    conn.close()

def get_stock_data(ticker):
    """Get stock price data for a specific ticker with limit to reduce memory."""
    conn = sqlite3.connect('stocks.db')
    try:
        query = """
        SELECT date, price, volume
        FROM stock_prices
        WHERE ticker = ?
        ORDER BY date DESC
        LIMIT 50
        """
        df = pd.read_sql_query(query, conn, params=(ticker,))
    except Exception as e:
        print(f"Error getting stock data: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def get_company_info(ticker):
    """Get company information for a specific ticker."""
    conn = sqlite3.connect('stocks.db')
    try:
        query = """
        SELECT ticker, company_name, industry, sector
        FROM companies
        WHERE ticker = ? COLLATE NOCASE
        """
        df = pd.read_sql_query(query, conn, params=(ticker,))
        result = df.to_dict('records')[0] if not df.empty else None
    except Exception as e:
        print(f"Error getting company info: {e}")
        result = None
    finally:
        conn.close()
    return result

def popular_companies():
    """Get a list of popular companies based on market cap with reduced memory usage."""
    conn = sqlite3.connect('stocks.db')
    try:
        query = """
        SELECT ticker, company_name, market_cap
        FROM companies
        ORDER BY market_cap DESC
        LIMIT 10
        """
        df = pd.read_sql_query(query, conn)
        result = df.to_dict('records')
    except Exception as e:
        print(f"Error getting popular companies: {e}")
        # Return fallback data if database query fails
        result = [
            {'ticker': 'AAPL', 'company_name': 'Apple Inc.', 'market_cap': 3000000000000},
            {'ticker': 'MSFT', 'company_name': 'Microsoft Corp.', 'market_cap': 2800000000000},
            {'ticker': 'GOOGL', 'company_name': 'Alphabet Inc.', 'market_cap': 1700000000000},
            {'ticker': 'AMZN', 'company_name': 'Amazon.com Inc.', 'market_cap': 1500000000000},
            {'ticker': 'TSLA', 'company_name': 'Tesla Inc.', 'market_cap': 800000000000}
        ]
    finally:
        conn.close()
    return result

def get_portfolio_summary():
    """Get current portfolio summary."""
    conn = sqlite3.connect('stocks.db')
    try:
        # Get latest portfolio value
        portfolio_query = """
        SELECT * FROM portfolio 
        ORDER BY date DESC 
        LIMIT 1
        """
        portfolio_df = pd.read_sql_query(portfolio_query, conn)
        
        # Get current holdings
        holdings_query = """
        SELECT * FROM holdings 
        WHERE shares > 0
        ORDER BY current_value DESC
        """
        holdings_df = pd.read_sql_query(holdings_query, conn)
        
        # Get recent trades
        trades_query = """
        SELECT * FROM trades 
        ORDER BY trade_date DESC 
        LIMIT 10
        """
        trades_df = pd.read_sql_query(trades_query, conn)
        
        # Get portfolio performance over time
        performance_query = """
        SELECT date, total_value, daily_return 
        FROM portfolio 
        ORDER BY date DESC 
        LIMIT 30
        """
        performance_df = pd.read_sql_query(performance_query, conn)
        
        portfolio_summary = {
            'current': portfolio_df.to_dict('records')[0] if not portfolio_df.empty else None,
            'holdings': holdings_df.to_dict('records'),
            'recent_trades': trades_df.to_dict('records'),
            'performance': performance_df.to_dict('records')
        }
        
    except Exception as e:
        print(f"Error getting portfolio summary: {e}")
        portfolio_summary = {
            'current': {'total_value': 10000.0, 'cash_balance': 10000.0, 'total_stocks_value': 0.0, 'daily_return': 0.0},
            'holdings': [],
            'recent_trades': [],
            'performance': []
        }
    finally:
        conn.close()
    
    return portfolio_summary

def simulate_trade(ticker, prediction, confidence, current_price):
    """Simulate a trade based on prediction."""
    conn = sqlite3.connect('stocks.db')
    try:
        cursor = conn.cursor()
        
        # Get current portfolio
        cursor.execute('SELECT cash_balance FROM portfolio ORDER BY date DESC LIMIT 1')
        cash_balance = cursor.fetchone()[0]
        
        # Simple trading strategy
        trade_amount = min(1000, cash_balance * 0.1)  # Max 10% of cash or $1000
        
        if prediction > current_price and confidence > 0.6:  # Buy signal
            shares_to_buy = trade_amount / current_price
            if cash_balance >= trade_amount:
                # Record trade
                cursor.execute('''
                    INSERT INTO trades (ticker, action, shares, price, total_amount, prediction, confidence, trade_date)
                    VALUES (?, 'BUY', ?, ?, ?, ?, ?, date('now'))
                ''', (ticker, shares_to_buy, current_price, trade_amount, prediction, confidence))
                
                # Update holdings
                cursor.execute('SELECT shares, avg_price FROM holdings WHERE ticker = ?', (ticker,))
                holding = cursor.fetchone()
                
                if holding:
                    old_shares, old_avg_price = holding
                    new_shares = old_shares + shares_to_buy
                    new_avg_price = ((old_shares * old_avg_price) + (shares_to_buy * current_price)) / new_shares
                    cursor.execute('''
                        UPDATE holdings 
                        SET shares = ?, avg_price = ?, current_price = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE ticker = ?
                    ''', (new_shares, new_avg_price, current_price, ticker))
                else:
                    cursor.execute('''
                        INSERT INTO holdings (ticker, shares, avg_price, current_price)
                        VALUES (?, ?, ?, ?)
                    ''', (ticker, shares_to_buy, current_price, current_price))
                
                # Update cash balance
                new_cash_balance = cash_balance - trade_amount
                cursor.execute('''
                    UPDATE portfolio 
                    SET cash_balance = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE date = (SELECT MAX(date) FROM portfolio)
                ''', (new_cash_balance,))
                
                conn.commit()
                return f"Bought {shares_to_buy:.2f} shares of {ticker} at ${current_price:.2f}"
        
        elif prediction < current_price and confidence > 0.6:  # Sell signal
            cursor.execute('SELECT shares FROM holdings WHERE ticker = ?', (ticker,))
            holding = cursor.fetchone()
            
            if holding and holding[0] > 0:
                shares_to_sell = holding[0] * 0.5  # Sell half the position
                sell_amount = shares_to_sell * current_price
                
                # Record trade
                cursor.execute('''
                    INSERT INTO trades (ticker, action, shares, price, total_amount, prediction, confidence, trade_date)
                    VALUES (?, 'SELL', ?, ?, ?, ?, ?, date('now'))
                ''', (ticker, shares_to_sell, current_price, sell_amount, prediction, confidence))
                
                # Update holdings
                new_shares = holding[0] - shares_to_sell
                if new_shares > 0:
                    cursor.execute('''
                        UPDATE holdings 
                        SET shares = ?, current_price = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE ticker = ?
                    ''', (new_shares, current_price, ticker))
                else:
                    cursor.execute('DELETE FROM holdings WHERE ticker = ?', (ticker,))
                
                # Update cash balance
                new_cash_balance = cash_balance + sell_amount
                cursor.execute('''
                    UPDATE portfolio 
                    SET cash_balance = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE date = (SELECT MAX(date) FROM portfolio)
                ''', (new_cash_balance,))
                
                conn.commit()
                return f"Sold {shares_to_sell:.2f} shares of {ticker} at ${current_price:.2f}"
        
        return "No trade executed (low confidence or insufficient conditions)"
        
    except Exception as e:
        print(f"Error simulating trade: {e}")
        return "Trade simulation failed"
    finally:
        conn.close()

def update_portfolio_value():
    """Update the total portfolio value."""
    conn = sqlite3.connect('stocks.db')
    try:
        cursor = conn.cursor()
        
        # Get current cash balance
        cursor.execute('SELECT cash_balance FROM portfolio ORDER BY date DESC LIMIT 1')
        cash_balance = cursor.fetchone()[0]
        
        # Calculate total stock value
        cursor.execute('SELECT SUM(shares * current_price) FROM holdings WHERE shares > 0')
        result = cursor.fetchone()
        total_stocks_value = result[0] if result[0] else 0.0
        
        total_value = cash_balance + total_stocks_value
        
        # Update portfolio
        cursor.execute('''
            UPDATE portfolio 
            SET total_value = ?, total_stocks_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE date = (SELECT MAX(date) FROM portfolio)
        ''', (total_value, total_stocks_value))
        
        conn.commit()
        return total_value
        
    except Exception as e:
        print(f"Error updating portfolio value: {e}")
        return 10000.0
    finally:
        conn.close()