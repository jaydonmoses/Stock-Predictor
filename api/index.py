import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Vercel environment variable
os.environ['VERCEL'] = '1'

# Import the Flask app
from app import app

# Vercel requires the Flask app to be accessible as 'app'
# This is the main entry point for Vercel
if __name__ == "__main__":
    app.run(debug=False)