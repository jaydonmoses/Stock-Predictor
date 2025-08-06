import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, jsonify
from stock_predictor import predict_next_close
from database import init_db, get_stock_data, get_company_info, popular_companies

app = Flask(__name__)

@app.route('/api/companies')
def get_companies():
    """API endpoint to get all companies for autocomplete"""
    conn = sqlite3.connect('stocks.db')
    companies = pd.read_sql_query("""
        SELECT ticker, company_name as name
        FROM companies
    """, conn)
    conn.close()
    return jsonify(companies.to_dict('records'))

# Initialize database on startup
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the home page or handle ticker submission."""
    companies = popular_companies()
    # Rename company_name to name to match the template
    for company in companies:
        company['name'] = company.pop('company_name')
    
    return render_template('index.html', companies=companies)


@app.route('/main', methods=['GET'])
def main():
    """Render the main page with stock prediction."""
    ticker = request.args.get('ticker')
    print(ticker)
    if not ticker:
        return redirect(url_for('index'))

    prediction = None
    direction = None
    error_message = None
    company_info = get_company_info(ticker)
    print(company_info)
    
    if company_info:
        result = predict_next_close(ticker)
        if result:
            prediction_data, last_close, confidence_score, feature_importance, graph_data = result
            direction = "rise" if prediction_data > last_close else "fall or stay the same"
            confidence_pct = round(confidence_score * 100, 2)
            
            # Sort feature importance for display
            feature_importance = dict(sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True))
        else:
            error_message = f"Could not get prediction for {ticker}. Data might be unavailable."
    else:
        error_message = f"Invalid ticker symbol: {ticker}"
    
    return render_template('main.html', 
                         prediction=prediction_data if not error_message else None,
                         direction=direction, 
                         ticker=ticker,
                         company=company_info,
                         confidence=confidence_pct if not error_message else None,
                         feature_importance=feature_importance if not error_message else None,
                         graph_data=graph_data if not error_message else None,
                         error=error_message)

@app.after_request
def add_header(response):
    # Cache static assets for 1 year
    if 'static' in response.headers.get('Content-Type', ''):
        response.cache_control.max_age = 31536000
        response.cache_control.public = True
    return response

if __name__ == '__main__':
    app.run(debug=True)