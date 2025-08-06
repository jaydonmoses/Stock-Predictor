import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Vercel environment variable
os.environ['VERCEL'] = '1'

# Import the Flask app
from app import app

# This is the entry point that Vercel will use
# The app variable will be automatically detected by Vercel