import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, jsonify
from stock_predictor import predict_next_close
from database import init_db, get_stock_data, get_company_info, popular_companies
from portfolio import Portfolio

app = Flask(__name__)

# Configure the app based on environment
import os
from config import config

config_name = 'vercel' if os.environ.get('VERCEL') else 'development'
app.config.from_object(config[config_name])
config[config_name].init_app(app)

@app.route('/api/companies')
def get_companies():
    """API endpoint to get all companies for autocomplete"""
    from database_config import get_db_path
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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

@app.route('/simulator')
def simulator():
    """Show the portfolio simulator dashboard."""
    portfolio = Portfolio()
    summary = portfolio.get_portfolio_summary()
    transactions = portfolio.get_transaction_history(limit=20)
    performance_data = portfolio.get_performance_data(days=30)
    
    # Create chart data for portfolio performance
    chart_data = {
        'dates': [entry['date'] for entry in reversed(performance_data)],
        'values': [entry['total_value'] for entry in reversed(performance_data)],
        'cash': [entry['cash_balance'] for entry in reversed(performance_data)],
        'stocks': [entry['stock_value'] for entry in reversed(performance_data)]
    }
    
    return render_template('simulator.html', 
                         summary=summary, 
                         transactions=transactions,
                         chart_data=chart_data)

@app.route('/api/simulate_trade', methods=['POST'])
def simulate_trade():
    """Execute a simulated trade."""
    portfolio = Portfolio()
    trade_result, message = portfolio.simulate_daily_trade()
    
    # Update portfolio history
    portfolio.update_portfolio_history()
    
    return jsonify({
        'success': trade_result is not None,
        'trade': trade_result,
        'message': message
    })

@app.route('/api/manual_trade', methods=['POST'])
def manual_trade():
    """Execute a manual trade."""
    data = request.get_json()
    
    ticker = data.get('ticker')
    action = data.get('action')  # 'buy' or 'sell'
    shares = int(data.get('shares', 0))
    
    if not ticker or not action or shares <= 0:
        return jsonify({'success': False, 'message': 'Invalid trade parameters'})
    
    # Get current stock price (using last close from prediction)
    result = predict_next_close(ticker)
    if not result:
        return jsonify({'success': False, 'message': f'Could not get price for {ticker}'})
    
    _, last_close, confidence, _, _ = result
    
    portfolio = Portfolio()
    success, message = portfolio.execute_trade(ticker, action, shares, last_close)
    
    # Update portfolio history
    portfolio.update_portfolio_history()
    
    return jsonify({
        'success': success,
        'message': message,
        'price': last_close
    })

@app.route('/api/portfolio_data')
def portfolio_data():
    """Get current portfolio data as JSON."""
    portfolio = Portfolio()
    summary = portfolio.get_portfolio_summary()
    return jsonify(summary)

@app.after_request
def add_header(response):
    # Cache static assets for 1 year
    if 'static' in response.headers.get('Content-Type', ''):
        response.cache_control.max_age = 31536000
        response.cache_control.public = True
    return response

if __name__ == '__main__':
    app.run(debug=True)