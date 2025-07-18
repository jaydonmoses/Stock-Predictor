from flask import Flask, render_template, request, redirect, url_for, jsonify
from stock_predictor import predict_next_close

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the home page."""
    if request.method == 'POST':
        ticker = request.form.get('ticker')  # Get ticker from form
        if not ticker:
            return jsonify({'message': 'No ticker provided'}), 400
        # Redirect to the main route, passing the ticker
        return redirect(url_for('main', ticker=ticker))
    return render_template('index.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    """Render the main page with stock prediction."""
    ticker = request.args.get('ticker')  # Get ticker from query parameters
    if not ticker:
        return "No ticker provided", 400

    prediction = None
    direction = None
    result = predict_next_close(ticker)  # Pass ticker to prediction function
    if result:
        prediction, last_close = result
        direction = "rise" if prediction > last_close else "fall or stay the same"

    return render_template('main.html', prediction=prediction, direction=direction, ticker=ticker)

if __name__ == '__main__':
    app.run(debug=True)
