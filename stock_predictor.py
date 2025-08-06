import pandas as pd
import yfinance as yf
import sqlite3
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import logging
import numpy as np
import plotly.graph_objects as go
import shap
import json

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
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
    x=historical_data['Date'],
    y=historical_data['Close'],
    name='Actual Price',
    line=dict(color='blue')))

    fig.add_trace(go.Scatter(
    x=predictions['Date'],  # Use the 'Date' column from the predictions DataFrame
    y=predictions['Predicted'],
    name='Predicted Price',
    line=dict(color='red', dash='dash')))
    
    fig.update_layout(
        title=f'{ticker} Stock Price - Actual vs Predicted',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_white'
    )
    
    return json.loads(fig.to_json())

def predict_next_close(ticker):
    try:
        logger.info(f"Downloading data for {ticker}")
        # Download stock data with auto_adjust explicitly set
        data = yf.download(ticker, start='2020-01-01', auto_adjust=True)
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

        # Add technical indicators
        loaded_data['SMA_5'] = loaded_data['Close'].rolling(window=5).mean()
        loaded_data['SMA_20'] = loaded_data['Close'].rolling(window=20).mean()
        loaded_data['RSI'] = calculate_rsi(loaded_data['Close'])
        
        # Drop rows with NaN values from the indicators
        loaded_data = loaded_data.dropna()
        
        # Features for prediction
        feature_columns = ['Open', 'High', 'Low', 'Volume', 'SMA_5', 'SMA_20', 'RSI']
        X = loaded_data[feature_columns]
        y = loaded_data['Close']

        # Check for sufficient data
        if len(y) < 30:  # Need sufficient data for training
            logger.error("Insufficient data points")
            return None
            
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        # Create and train the model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Calculate feature importance using SHAP
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        feature_importance = dict(zip(feature_columns, np.abs(shap_values).mean(axis=0)))

        # Normalize the feature importance values
        total_importance = sum(feature_importance.values())
        if total_importance > 0:
            normalized_importance = {key: value / total_importance for key, value in feature_importance.items()}
        else:
            normalized_importance = feature_importance  # Avoid division by zero
        
        # Make predictions with confidence intervals
        predictions = pd.DataFrame(index=X_test.index)
        predictions['Date'] = loaded_data.loc[X_test.index]['Date']
        predictions['Predicted'] = model.predict(X_test)
        
        # Calculate prediction intervals using random forest's built-in variance
        predictions_all = np.array([tree.predict(X_test) for tree in model.estimators_])
        predictions['Lower'] = np.percentile(predictions_all, 5, axis=0)
        predictions['Upper'] = np.percentile(predictions_all, 95, axis=0)
        
        # Calculate confidence score
        confidence_score = 1.0 - (predictions['Upper'] - predictions['Lower']) / predictions['Predicted']
        
        # Generate graph data
        graph_data = create_stock_graph(loaded_data, predictions, ticker)

        # Make prediction for next day using all available data
        model_final = RandomForestRegressor(n_estimators=100, random_state=42)
        model_final.fit(X, y)  # Train on all data
        
        # Prepare last data point for prediction
        last_data = X.iloc[-1:]
        
        # Make prediction
        prediction = model_final.predict(last_data)[0]
        last_close = y.iloc[-1]
        
        # Calculate confidence score for the final prediction
        predictions_all_final = np.array([tree.predict(last_data) for tree in model_final.estimators_])
        confidence_interval = np.percentile(predictions_all_final, [5, 95])
        confidence_score = 1.0 - (confidence_interval[1] - confidence_interval[0]) / prediction
        
        # Average confidence score
        mean_confidence = np.mean(confidence_score)
        
        logger.info(f"Prediction: {prediction:.2f}, Last Close: {last_close:.2f}")
        return prediction, last_close, mean_confidence, normalized_importance, graph_data

    except Exception as e:
        logger.error(f"Error in predict_next_close: {str(e)}")
        return None

if __name__ == "__main__":
    result = predict_next_close('AAPL')
    print(f"Prediction result: {result}")