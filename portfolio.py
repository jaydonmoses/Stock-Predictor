import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
from stock_predictor import predict_next_close
from database_config import get_portfolio_db_path, get_db_path

class Portfolio:
    def __init__(self, db_path=None):
        self.db_path = db_path or get_portfolio_db_path()
        self.init_portfolio_db()
    
    def init_portfolio_db(self):
        """Initialize the portfolio database with necessary tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Portfolio table to track overall portfolio stats
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 10000.0,
                total_value REAL DEFAULT 10000.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Holdings table to track current stock positions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY,
                ticker TEXT NOT NULL,
                shares REAL NOT NULL,
                avg_cost REAL NOT NULL,
                current_price REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transactions table to track all buy/sell operations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL, -- 'buy' or 'sell'
                shares REAL NOT NULL,
                price REAL NOT NULL,
                total_cost REAL NOT NULL,
                prediction REAL,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Portfolio history for tracking performance over time
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_history (
                id INTEGER PRIMARY KEY,
                date DATE NOT NULL,
                total_value REAL NOT NULL,
                cash_balance REAL NOT NULL,
                stock_value REAL NOT NULL,
                daily_return REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize portfolio if it doesn't exist
        cursor.execute('SELECT COUNT(*) FROM portfolio')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO portfolio (balance, total_value) VALUES (10000.0, 10000.0)')
        
        conn.commit()
        conn.close()
    
    def get_portfolio_summary(self):
        """Get current portfolio summary."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current portfolio stats
        cursor.execute('SELECT balance, total_value FROM portfolio WHERE id = 1')
        portfolio_data = cursor.fetchone()
        
        if not portfolio_data:
            conn.close()
            return None
        
        balance, total_value = portfolio_data
        
        # Get current holdings
        cursor.execute('''
            SELECT ticker, shares, avg_cost, current_price, 
                   (shares * COALESCE(current_price, avg_cost)) as market_value
            FROM holdings 
            WHERE shares > 0
        ''')
        holdings = cursor.fetchall()
        
        # Calculate total stock value
        stock_value = sum([holding[4] for holding in holdings])
        
        conn.close()
        
        return {
            'cash_balance': balance,
            'stock_value': stock_value,
            'total_value': balance + stock_value,
            'holdings': holdings
        }
    
    def execute_trade(self, ticker, action, shares, price, prediction=None, confidence=None):
        """Execute a buy or sell trade."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        total_cost = shares * price
        
        if action == 'buy':
            # Check if we have enough cash
            cursor.execute('SELECT balance FROM portfolio WHERE id = 1')
            current_balance = cursor.fetchone()[0]
            
            if current_balance < total_cost:
                conn.close()
                return False, "Insufficient funds"
            
            # Update cash balance
            new_balance = current_balance - total_cost
            cursor.execute('UPDATE portfolio SET balance = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1', (new_balance,))
            
            # Update or insert holding
            cursor.execute('SELECT shares, avg_cost FROM holdings WHERE ticker = ?', (ticker,))
            existing_holding = cursor.fetchone()
            
            if existing_holding:
                existing_shares, existing_avg_cost = existing_holding
                new_shares = existing_shares + shares
                new_avg_cost = ((existing_shares * existing_avg_cost) + total_cost) / new_shares
                cursor.execute('''
                    UPDATE holdings 
                    SET shares = ?, avg_cost = ?, current_price = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE ticker = ?
                ''', (new_shares, new_avg_cost, price, ticker))
            else:
                cursor.execute('''
                    INSERT INTO holdings (ticker, shares, avg_cost, current_price) 
                    VALUES (?, ?, ?, ?)
                ''', (ticker, shares, price, price))
        
        elif action == 'sell':
            # Check if we have enough shares
            cursor.execute('SELECT shares FROM holdings WHERE ticker = ?', (ticker,))
            existing_holding = cursor.fetchone()
            
            if not existing_holding or existing_holding[0] < shares:
                conn.close()
                return False, "Insufficient shares"
            
            # Update cash balance
            cursor.execute('SELECT balance FROM portfolio WHERE id = 1')
            current_balance = cursor.fetchone()[0]
            new_balance = current_balance + total_cost
            cursor.execute('UPDATE portfolio SET balance = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1', (new_balance,))
            
            # Update holding
            new_shares = existing_holding[0] - shares
            if new_shares <= 0:
                cursor.execute('DELETE FROM holdings WHERE ticker = ?', (ticker,))
            else:
                cursor.execute('''
                    UPDATE holdings 
                    SET shares = ?, current_price = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE ticker = ?
                ''', (new_shares, price, ticker))
        
        # Record transaction
        cursor.execute('''
            INSERT INTO transactions (ticker, action, shares, price, total_cost, prediction, confidence) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, action, shares, price, total_cost, prediction, confidence))
        
        conn.commit()
        conn.close()
        
        return True, f"Successfully {action} {shares} shares of {ticker} at ${price:.2f}"
    
    def simulate_daily_trade(self):
        """Simulate a daily trade based on model predictions."""
        # Get a random stock from our holdings or popular stocks
        stocks_db_path = get_db_path()
        conn = sqlite3.connect(stocks_db_path)
        cursor = conn.cursor()
        
        # Get popular stocks for potential trades
        cursor.execute('SELECT ticker FROM companies ORDER BY market_cap DESC LIMIT 20')
        popular_tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not popular_tickers:
            return None, "No stocks available for trading"
        
        # Try to get prediction for a random stock
        import random
        ticker = random.choice(popular_tickers)
        
        result = predict_next_close(ticker)
        if not result:
            return None, f"Could not get prediction for {ticker}"
        
        prediction, last_close, confidence, _, _ = result
        
        # Determine trade action based on prediction
        predicted_return = (prediction - last_close) / last_close
        
        # Trading logic
        if predicted_return > 0.02 and confidence > 0.6:  # Predicted rise > 2% with good confidence
            action = 'buy'
            # Use a portion of available cash
            portfolio_summary = self.get_portfolio_summary()
            if portfolio_summary:
                max_investment = portfolio_summary['cash_balance'] * 0.1  # Use 10% of cash
                shares = int(max_investment / last_close)
                if shares > 0:
                    success, message = self.execute_trade(ticker, action, shares, last_close, prediction, confidence)
                    return {'action': action, 'ticker': ticker, 'shares': shares, 'price': last_close, 
                           'prediction': prediction, 'confidence': confidence, 'success': success, 'message': message}, message
        
        elif predicted_return < -0.02:  # Predicted fall > 2%
            # Check if we have this stock to sell
            portfolio_summary = self.get_portfolio_summary()
            if portfolio_summary:
                for holding in portfolio_summary['holdings']:
                    if holding[0] == ticker and holding[1] > 0:  # ticker and shares > 0
                        action = 'sell'
                        shares = int(holding[1] * 0.5)  # Sell 50% of holdings
                        if shares > 0:
                            success, message = self.execute_trade(ticker, action, shares, last_close, prediction, confidence)
                            return {'action': action, 'ticker': ticker, 'shares': shares, 'price': last_close, 
                                   'prediction': prediction, 'confidence': confidence, 'success': success, 'message': message}, message
        
        return None, f"No trade executed for {ticker} (predicted return: {predicted_return:.2%}, confidence: {confidence:.2%})"
    
    def get_transaction_history(self, limit=50):
        """Get recent transaction history."""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT ticker, action, shares, price, total_cost, prediction, confidence, timestamp
            FROM transactions 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        
        return df.to_dict('records')
    
    def update_portfolio_history(self):
        """Update daily portfolio history for performance tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current portfolio value
        portfolio_summary = self.get_portfolio_summary()
        if not portfolio_summary:
            conn.close()
            return
        
        today = datetime.now().date()
        total_value = portfolio_summary['total_value']
        cash_balance = portfolio_summary['cash_balance']
        stock_value = portfolio_summary['stock_value']
        
        # Calculate daily return
        cursor.execute('''
            SELECT total_value FROM portfolio_history 
            WHERE date < ? 
            ORDER BY date DESC 
            LIMIT 1
        ''', (today,))
        
        previous_value = cursor.fetchone()
        daily_return = 0
        if previous_value:
            daily_return = (total_value - previous_value[0]) / previous_value[0]
        
        # Insert or update today's record
        cursor.execute('''
            INSERT OR REPLACE INTO portfolio_history 
            (date, total_value, cash_balance, stock_value, daily_return) 
            VALUES (?, ?, ?, ?, ?)
        ''', (today, total_value, cash_balance, stock_value, daily_return))
        
        conn.commit()
        conn.close()
    
    def get_performance_data(self, days=30):
        """Get portfolio performance data for charting."""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT date, total_value, cash_balance, stock_value, daily_return
            FROM portfolio_history 
            ORDER BY date DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(days,))
        conn.close()
        
        return df.to_dict('records')