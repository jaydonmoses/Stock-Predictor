import pandas as pd
import yfinance as yf
import sqlite3
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import logging
import numpy as np
import json
import gc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def create_stock_graph(historical_data, predictions, ticker):
    """Create a lightweight graph representation without heavy plotting libraries"""
    # Return lightweight data structure instead of full plotly figure
    graph_data = {
        'ticker': ticker,
        'historical': {
            'dates': historical_data['Date'].tail(30).tolist(),  # Only last 30 days
            'prices': historical_data['Close'].tail(30).tolist()
        },
        'predictions': {
            'dates': predictions['Date'].tolist()[-10:] if len(predictions) > 10 else predictions['Date'].tolist(),  # Only last 10 predictions
            'prices': predictions['Predicted'].tolist()[-10:] if len(predictions) > 10 else predictions['Predicted'].tolist()
        }
    }
    return graph_data

def predict_next_close(ticker):
    """Memory-optimized stock prediction function"""
    try:
        logger.info(f"Downloading data for {ticker}")
        # Download only recent data to reduce memory usage (1 year instead of 5+ years)
        data = yf.download(ticker, period='1y', auto_adjust=True)
        if data.empty:
            logger.error(f"No data downloaded for {ticker}")
            return None

        logger.info(f"Downloaded data shape: {data.shape}")

        # Clean up column names
        data.columns = data.columns.get_level_values(0) if hasattr(data.columns, 'levels') else data.columns
        
        # Use memory mapping for database operations
        db_path = "stocks.db"
        with sqlite3.connect(db_path) as conn:
            data.reset_index(inplace=True)
            # Only store essential columns to save space
            essential_data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
            essential_data.to_sql(f"{ticker}_temp", conn, if_exists='replace', index=False)
            
            # Load data back with chunking for large datasets
            loaded_data = pd.read_sql_query(f"SELECT * FROM {ticker}_temp", conn)
            
            # Clean up temp table immediately
            conn.execute(f"DROP TABLE IF EXISTS {ticker}_temp")

        # Convert to numeric and handle errors efficiently
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_cols:
            loaded_data[col] = pd.to_numeric(loaded_data[col], errors='coerce')

        # Add minimal technical indicators (reduce memory footprint)
        loaded_data['SMA_5'] = loaded_data['Close'].rolling(window=5).mean()
        loaded_data['RSI'] = calculate_rsi(loaded_data['Close'], period=14)
        
        # Drop intermediate calculations from memory
        del data
        gc.collect()
        
        # Drop rows with NaN values
        loaded_data = loaded_data.dropna()
        
        # Use fewer features to reduce model complexity and memory
        feature_columns = ['Open', 'High', 'Low', 'Volume', 'SMA_5', 'RSI']
        X = loaded_data[feature_columns].copy()
        y = loaded_data['Close'].copy()

        # Check for sufficient data
        if len(y) < 30:
            logger.error("Insufficient data points")
            return None
            
        # Use smaller train/test split and simpler model
        test_size = min(0.2, 50/len(y))  # Max 50 test samples or 20%
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
        
        # Use smaller, more memory-efficient model
        model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Calculate simple feature importance without SHAP (memory heavy)
        feature_importance = dict(zip(feature_columns, model.feature_importances_))
        
        # Make predictions for graph (limit to recent data only)
        recent_indices = X_test.index[-min(20, len(X_test)):]  # Only last 20 predictions
        X_test_recent = X_test.loc[recent_indices]
        
        predictions = pd.DataFrame(index=recent_indices)
        predictions['Date'] = loaded_data.loc[recent_indices, 'Date'].values
        predictions['Predicted'] = model.predict(X_test_recent)
        
        # Generate lightweight graph data
        graph_data = create_stock_graph(loaded_data, predictions, ticker)
        
        # Make prediction for next day using the trained model (no retraining)
        last_data = X.iloc[-1:].copy()
        prediction = model.predict(last_data)[0]
        last_close = y.iloc[-1]
        
        # Calculate simple confidence score based on recent prediction accuracy
        if len(X_test_recent) > 0:
            recent_predictions = model.predict(X_test_recent)
            recent_actual = y.loc[recent_indices].values
            mae = np.mean(np.abs(recent_predictions - recent_actual))
            confidence_score = max(0.1, 1.0 - (mae / np.mean(recent_actual)))
        else:
            confidence_score = 0.5  # Default confidence
        
        # Clean up memory
        del loaded_data, X, y, X_train, X_test, y_train, y_test
        gc.collect()
        
        logger.info(f"Prediction: {prediction:.2f}, Last Close: {last_close:.2f}")
        return prediction, last_close, confidence_score, feature_importance, graph_data

    except Exception as e:
        logger.error(f"Error in predict_next_close: {str(e)}")
        return None

if __name__ == "__main__":
    result = predict_next_close('AAPL')
    print(f"Prediction result: {result}")