import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
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

    naive_pred = y.iloc[-2]  # use yesterday's close as the naive prediction

    metrics = evaluate_prediction(last_close, prediction, naive_pred)

    return prediction, metrics

def evaluate_prediction(y_true, y_pred, naive_pred):
    """
    Evaluates prediction performance using MAE, relative error, and naive baseline comparison.
    
    Parameters:
        y_true (float): The actual close value.
        y_pred (float): The predicted close value.
        naive_pred (float): The baseline prediction (e.g., yesterday's close).
    
    Returns:
        dict: Dictionary containing MAE, relative MAE, baseline MAE, and improvement.
    """
    mae = mean_absolute_error([y_true], [y_pred])
    rel_mae = (mae / y_true) * 100 if y_true != 0 else float('inf')
    naive_mae = mean_absolute_error([y_true], [naive_pred])
    improvement = naive_mae - mae
    beats_baseline = mae < naive_mae

    return {
        "mae": mae,
        "relative_mae_percent": rel_mae,
        "naive_mae": naive_mae,
        "improvement": improvement,
        "beats_baseline": beats_baseline
    }
