import pandas as pd
import yfinance as yf
import sqlite3
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def predict_next_close(ticker):
    try:
        logger.info(f"Downloading data for {ticker}")
        # Download stock data with auto_adjust explicitly set
        data = yf.download(ticker, start='2020-01-01', end='2023-12-31', auto_adjust=True)
        if data.empty:
            logger.error(f"No data downloaded for {ticker}")
            return None

        logger.info(f"Downloaded data shape: {data.shape}")

        # Clean up column names before saving to database
        data = data.rename(columns={
            f'Close': 'Close',
            f'Open': 'Open',
            f'High': 'High',
            f'Low': 'Low',
            f'Volume': 'Volume'
        })
        
        # Save to SQLite database
        db_path = "stocks.db"  # Changed path to match app.py
        conn = sqlite3.connect(db_path)
        data.reset_index(inplace=True)
        data.to_sql(ticker, conn, if_exists='replace', index=False)

        # Load data and clean column names
        query = f"SELECT * FROM {ticker}"
        loaded_data = pd.read_sql_query(query, conn)
        conn.close()

        # Clean up column names after loading
        loaded_data.columns = [col.split(',')[0].strip("(' )") for col in loaded_data.columns]
        logger.info(f"Cleaned columns: {loaded_data.columns.tolist()}")

        # Check required columns
        required_columns = ['Close', 'Open', 'High', 'Low', 'Volume']
        missing_cols = [col for col in required_columns if col not in loaded_data.columns]
        if missing_cols:
            logger.error(f"Missing columns: {missing_cols}")
            return None

        # Convert all relevant columns to numeric and handle any conversion errors
        for col in required_columns:
            loaded_data[col] = pd.to_numeric(loaded_data[col], errors='coerce')
            null_count = loaded_data[col].isnull().sum()
            if null_count > 0:
                logger.warning(f"Column {col} has {null_count} null values")

        # Features for prediction
        X = loaded_data[['Open', 'High', 'Low', 'Volume']]
        y = loaded_data['Close']

        # Check for sufficient data
        if len(y) < 2:  # Need at least 2 rows for training and prediction
            logger.error("Insufficient data points")
            return None

        # Remove any rows with NaN values
        valid_rows = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_rows]
        y = y[valid_rows]

        if X.empty or len(y) < 2:
            logger.error("No valid data after cleaning")
            return None

        # Train model on all data except last row
        train_X = X.iloc[:-1]
        train_y = y.iloc[:-1]
        test_X = X.iloc[[-1]]

        logger.info(f"Training data shape: {train_X.shape}")
        
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(train_X, train_y)
        
        prediction = rf_model.predict(test_X)[0]
        last_close = y.iloc[-1]
        
        logger.info(f"Prediction: {prediction:.2f}, Last Close: {last_close:.2f}")
        return prediction, last_close

    except Exception as e:
        logger.error(f"Error in predict_next_close: {str(e)}")
        return None

if __name__ == "__main__":
    result = predict_next_close('AAPL')
    print(f"Prediction result: {result}")