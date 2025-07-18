import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

def predict_next_close(ticker):
    # Download stock data
    data = yf.download(ticker, start='2020-01-01', end='2023-01-01')
    if data.empty:
        return None

    # Save to a fixed CSV file and reload
    csv_path = "stock_data.csv"
    data.to_csv(csv_path)
    loaded_data = pd.read_csv(csv_path)

    # Remove 'Unnamed: 0' column if present
    if 'Unnamed: 0' in loaded_data.columns:
        loaded_data = loaded_data.drop(columns=['Unnamed: 0'])

    # Check required columns
    required_columns = ['Close', 'Open', 'High', 'Low', 'Volume']
    missing_cols = [col for col in required_columns if col not in loaded_data.columns]
    if missing_cols:
        return None

    # Target variable
    y = loaded_data['Close']
    y = pd.to_numeric(y, errors='coerce')

    # Features for prediction
    features = ['Open', 'High', 'Low', 'Volume']
    X = loaded_data[features]
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors='coerce')
    X = X.select_dtypes(include='number')
    if X.empty:
        return None

    # Impute missing values in features
    feature_imputer = SimpleImputer()
    X = pd.DataFrame(feature_imputer.fit_transform(X), columns=X.columns)

    # Impute missing values in target
    target_imputer = SimpleImputer()
    y = pd.Series(target_imputer.fit_transform(y.values.reshape(-1, 1)).ravel(), name='Close')

    # Train model on all data except last row
    train_X = X.iloc[:-1]
    train_y = y.iloc[:-1]
    test_X = X.iloc[[-1]]  # last row for prediction

    rf_model = RandomForestRegressor(random_state=1)
    rf_model.fit(train_X, train_y)
    prediction = rf_model.predict(test_X)[0]
    last_close = y.iloc[-1]
    return prediction, last_close