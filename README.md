# 🚀 AI Stock Predictor

A sophisticated machine learning-powered stock prediction application with an integrated AI trading simulator. Built with Flask, scikit-learn, and modern web technologies.

## 🌟 Live Demo

**Try it now:** [https://stock-predictor-epf9.onrender.com](https://stock-predictor-epf9.onrender.com)

## 📋 Features

### 🤖 AI-Powered Stock Prediction
- **Machine Learning Models**: Random Forest algorithms with technical indicators
- **Real-time Data**: Live stock data via Yahoo Finance API
- **Technical Analysis**: RSI, Moving Averages, and price momentum indicators
- **Confidence Scoring**: AI confidence levels for each prediction
- **Interactive Charts**: Beautiful Chart.js visualizations

### 💰 Virtual Trading Simulator
- **$10,000 Starting Balance**: Realistic portfolio simulation
- **Intelligent Trading Bot**: Automated buy/sell decisions based on AI predictions
- **Risk Management**: Position sizing and stop-loss mechanisms  
- **Portfolio Tracking**: Real-time P&L, holdings, and performance metrics
- **Trade History**: Detailed transaction logs with reasoning

### 🎨 Modern User Interface
- **Glassmorphism Design**: Modern, elegant UI with gradient backgrounds
- **Company Logos**: Real company logos via Clearbit API
- **Responsive Layout**: Works perfectly on desktop and mobile
- **Real-time Updates**: Dynamic portfolio updates and live predictions
- **Intuitive Navigation**: Easy-to-use search and autocomplete

## 🛠️ Technology Stack

### Backend
- **Python 3.9+** - Core application language
- **Flask** - Lightweight web framework
- **SQLite** - Embedded database for portfolio data
- **scikit-learn** - Machine learning algorithms
- **pandas** - Data manipulation and analysis
- **yfinance** - Yahoo Finance API wrapper

### Frontend
- **HTML5/CSS3** - Modern web standards
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Interactive chart visualizations
- **JavaScript (ES6+)** - Dynamic user interactions

### Deployment
- **Render** - Cloud platform deployment
- **Gunicorn** - WSGI HTTP Server
- **Memory-optimized** - Configured for free tier hosting

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jaydonmoses/Stock-Predictor.git
   cd Stock-Predictor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

### Dependencies

```
Flask
gunicorn
numpy
pandas
yfinance
scikit-learn
```

## 📊 How It Works

### 1. Stock Analysis Process
1. **Data Collection**: Downloads 1 year of historical stock data
2. **Feature Engineering**: Calculates technical indicators (RSI, SMA, etc.)
3. **Model Training**: Random Forest model learns from historical patterns
4. **Prediction**: Generates next-day price prediction with confidence score
5. **Visualization**: Creates interactive charts showing historical vs predicted prices

### 2. AI Trading Simulation
1. **Signal Generation**: AI evaluates buy/sell conditions based on:
   - Prediction vs current price
   - Confidence score (>60% threshold)
   - Available cash balance
2. **Trade Execution**: Simulates realistic trades with:
   - Position sizing (max 10% of portfolio)
   - Transaction costs consideration
   - Risk management rules
3. **Portfolio Updates**: Real-time tracking of:
   - Total portfolio value
   - Individual stock positions
   - Cash vs equity allocation
   - Performance metrics

## 🎯 Trading Strategy

The AI trading bot uses a systematic approach:

### Buy Signals
- Predicted price > Current price
- Confidence score > 60%
- Sufficient cash available
- Position sizing: Max $1000 or 10% of cash

### Sell Signals  
- Predicted price < Current price
- Confidence score > 60%
- Existing position available
- Sells 50% of position for risk management

## 📈 Performance Features

### Portfolio Dashboard
- **Real-time Valuation**: Live portfolio worth tracking
- **Asset Allocation**: Cash vs stocks breakdown
- **Holdings Overview**: Individual stock positions with P&L
- **Trade History**: Detailed transaction log
- **Performance Metrics**: Daily returns and growth tracking

### Risk Management
- **Position Limits**: Maximum exposure per stock
- **Confidence Filtering**: Only high-confidence trades
- **Partial Selling**: Gradual position reduction
- **Cash Reserves**: Maintains liquidity for opportunities

## 🔧 Configuration

### Memory Optimization
The application is optimized for deployment on free hosting tiers:
- **Reduced data periods** (1 year vs 5+ years)
- **Simplified models** (50 trees vs 100)
- **Chunked processing** for large datasets
- **Garbage collection** after operations
- **Connection pooling** for database operations

### Environment Variables
```bash
PYTHON_VERSION=3.9.16
PYTHONUNBUFFERED=1
WEB_CONCURRENCY=1
```

## 🚀 Deployment

### Render Deployment
1. **Connect Repository**: Link your GitHub repository to Render
2. **Configure Build**: Uses `render.yaml` configuration
3. **Environment Setup**: Python 3.9 with optimized settings
4. **Auto-deploy**: Automatic deployments on code changes

### Local Development
```bash
# Development server
python app.py

# Production server (optional)
gunicorn --bind 0.0.0.0:5000 app:app
```

## 📁 Project Structure

```
Stock-Predictor/
├── app.py                 # Main Flask application
├── stock_predictor.py     # ML prediction engine
├── database.py           # Database operations & portfolio logic
├── requirements.txt      # Python dependencies
├── render.yaml          # Deployment configuration
├── Procfile             # Process configuration
├── runtime.txt          # Python version specification
├── templates/           # HTML templates
│   ├── index.html       # Home page
│   ├── main.html        # Prediction results
│   └── portfolio.html   # Portfolio dashboard
├── static/             # Static assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── *.csv           # Company and stock data
└── stocks.db           # SQLite database (generated)
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit changes**: `git commit -m 'Add AmazingFeature'`
4. **Push to branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for **educational and entertainment purposes only**. It is not intended as financial advice. Always do your own research and consult with financial professionals before making investment decisions. Past performance does not guarantee future results.

## 🔮 Future Enhancements

- **Real-time WebSocket updates** for live price streaming
- **Advanced ML models** (LSTM, Transformer architectures)
- **Options trading simulation** with Greeks calculations
- **Social features** with leaderboards and competitions
- **Portfolio optimization** using Modern Portfolio Theory
- **News sentiment analysis** integration
- **Mobile app** development

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/jaydonmoses/Stock-Predictor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jaydonmoses/Stock-Predictor/discussions)
- **Email**: [Support Contact]

---

**Built with ❤️ by [Jaydon Moses](https://github.com/jaydonmoses)**

*Experience the future of AI-powered investing!* 🚀📈
