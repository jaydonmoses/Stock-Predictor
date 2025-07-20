import csv
from flask import Flask, render_template, request, redirect, url_for, jsonify
from stock_predictor import predict_next_close
import os
from company_parser import load_companies, return_company_info, sort_by_market_cap, get_company_by_ticker, get_company_by_name
from dotenv import load_dotenv

# Load environment variables from .env file at the very beginning
load_dotenv()

app = Flask(__name__)

# Access your Logo.dev API key from environment variables
LOGO_DEV_API_KEY = os.getenv('LOGO_DEV_API_KEY')

if not LOGO_DEV_API_KEY:
    print("WARNING: LOGO_DEV_API_KEY not found in environment variables or .env file!")
    print("Logos might not load correctly without an API key. Ensure LOGO_DEV_API_KEY is set in your .env file.")

# Load all companies data once when the app starts
# The path 'static/companies.csv' is relative to app.py's location.
ALL_COMPANIES_DATA_LIST = load_companies('static/companies.csv')

# Create a dictionary for quick lookup by ticker (for internal use)
ALL_COMPANIES_DATA_DICT = {company['ticker']: company for company in ALL_COMPANIES_DATA_LIST}


@app.route('/', methods=['GET'])
def index():
    """Render the home page with search and popular companies."""
    # Sort popular companies (e.g., by market cap if available, or just alphabetically)
    # If your CSV has a 'market_cap' column, you can use sort_by_market_cap.
    # Otherwise, sort by name or just pass ALL_COMPANIES_DATA_LIST directly.
    
    # For now, let's sort alphabetically by name for popular companies display
    sorted_companies = sorted(ALL_COMPANIES_DATA_LIST, key=lambda x: x.get('name', ''))

    # Prepare companies for the frontend (autocomplete and popular companies list)
    # Ensure each company object has 'name', 'ticker', 'website', and 'logo_url'
    companies_for_frontend = []
    for company in sorted_companies:
        logo_url = f"https://logo.clearbit.com/{company.get('website', '')}" if company.get('website') else '/static/default-logo.png'
        companies_for_frontend.append({
            'name': company.get('name'),
            'ticker': company.get('ticker'),
            'website': company.get('website'),
            'logo_url': logo_url
        })

    return render_template('index.html', companies=companies_for_frontend)


@app.route('/main', methods=['GET'])
def main():
    """Render the main page with stock prediction."""
    ticker_or_name = request.args.get('ticker', '').strip()
    if not ticker_or_name:
        return redirect(url_for('index'))

    prediction = None
    metrics = None
    error_message = None
    company_details = {
        "name": ticker_or_name,
        "logo_url": "/static/default-logo.png",
        "website": "",
        "description": "Company details not available.",
        "ceo": ""
    }

    # Use return_company_info from company_parser to get all details
    # Pass ALL_COMPANIES_DATA_LIST as the first argument
    found_company_info = return_company_info(ALL_COMPANIES_DATA_LIST, ticker_or_name)

    if found_company_info:
        company_details = found_company_info
        # Use the ticker from the found company info for prediction
        actual_ticker_for_prediction = company_details.get('ticker') or company_details.get('Symbol')
        if not actual_ticker_for_prediction:
            error_message = f"Could not determine ticker for '{ticker_or_name}'."
    else:
        error_message = f"Company '{ticker_or_name}' not found. Please check the ticker or company name."

    if not error_message and actual_ticker_for_prediction:
        result = predict_next_close(actual_ticker_for_prediction)
        if result:
            prediction, metrics = result
        else:
            error_message = f"Could not get prediction for {actual_ticker_for_prediction}. It might not be a valid ticker or data is unavailable."
    elif not actual_ticker_for_prediction:
        # If actual_ticker_for_prediction was not set due to an error, ensure error_message is set
        if not error_message: # Prevent overwriting a more specific error
            error_message = f"Invalid company identifier: '{ticker_or_name}'."


    # Format metrics if available
    formatted_metrics = format_metrics(metrics) if metrics else None
    
    # Pass the original input 'ticker_or_name' for display, and the prediction/error
    return render_template('main.html',
                           prediction=prediction,
                           metrics=formatted_metrics, # Pass formatted metrics
                           ticker=ticker_or_name, # Original input for display
                           error=error_message,
                           company_details=company_details
                           )

@app.after_request
def add_header(response):
    """Add cache control headers to static files."""
    if 'static' in response.headers.get('Content-Type', ''):
        response.cache_control.max_age = 31536000
        response.cache_control.public = True
    return response

def format_metrics(metrics):
    """Formats the prediction metrics into a readable HTML string."""
    if not metrics:
        return "No additional metrics available."
    
    return (
        f"<div class='text-left'>"
        f"<p><strong>Model MAE:</strong> ${metrics['mae']:.2f} ({metrics['relative_mae_percent']:.2f}%)</p>"
        f"<p><strong>Naive MAE:</strong> ${metrics['naive_mae']:.2f}</p>"
        f"<p><strong>Improvement:</strong> ${metrics['improvement']:.2f}</p>"
        f"<p>{'✅ Model beats baseline' if metrics['beats_baseline'] else '❌ Model underperforms baseline'}</p>"
        f"</div>"
    )

if __name__ == '__main__':
    app.run(debug=True)
