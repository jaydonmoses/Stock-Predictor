import csv
from flask import Flask, render_template, request, redirect, url_for, jsonify
from stock_predictor import predict_next_close
from flask import send_from_directory

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the home page or handle ticker submission."""
    companies = []

    with open('companies.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            companies.append({
                'ticker': row['ticker'],
                'name': row['company name'],
                'logo': row['logo']
            })

    return render_template('index.html', companies=companies)


@app.route('/main', methods=['GET'])
def main():
    """Render the main page with stock prediction."""
    ticker = request.args.get('ticker') # This could now be a company name or ticker
    if not ticker:
        return redirect(url_for('index'))

    prediction = None
    direction = None
    error_message = None
    
    actual_ticker_for_prediction = ticker 

    if not error_message:
        result = predict_next_close(actual_ticker_for_prediction)
        if result:
            prediction, last_close = result
            direction = "rise" if prediction > last_close else "fall or stay the same"
        else:
            error_message = f"Could not get prediction for {actual_ticker_for_prediction}. It might not be a valid ticker or data is unavailable."
    
    # Pass the original input 'ticker' for display, and the prediction/error
    return render_template('main.html', prediction=prediction, direction=direction, ticker=ticker, error=error_message)

@app.after_request
def add_header(response):
    # Cache static assets for 1 year
    if 'static' in response.headers.get('Content-Type', ''):
        response.cache_control.max_age = 31536000
        response.cache_control.public = True
    return response

if __name__ == '__main__':
    app.run(debug=True)