# Vercel Deployment Guide

## Pre-deployment Checklist

### ✅ Completed Optimizations

1. **Serverless Architecture**: Moved main app to `api/index.py` for Vercel compatibility
2. **Database Handling**: Implemented serverless-friendly database management using `/tmp` storage
3. **Static Files**: Fixed all static file paths to use absolute paths (`/static/`)
4. **API-based Logos**: Using external APIs instead of storing logo files locally
5. **Dependencies**: Added all required packages with specific versions
6. **Configuration**: Environment-aware configuration for development/production

### 📁 Project Structure for Vercel

```
├── api/
│   └── index.py          # Main Vercel entry point
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   ├── companies.csv     # Company data
│   └── stock_data.csv    # Stock price data
├── templates/
│   ├── index.html
│   ├── main.html
│   └── simulator.html
├── app.py               # Main Flask application
├── portfolio.py         # Portfolio management
├── database.py          # Database functions
├── database_config.py   # Serverless database config
├── stock_predictor.py   # ML prediction model
├── config.py           # Environment configuration
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version
├── vercel.json         # Vercel configuration
└── .vercelignore       # Files to exclude from deployment
```

## Deployment Steps

### 1. Connect to Vercel

1. Visit [vercel.com](https://vercel.com)
2. Sign up/Login with GitHub
3. Click "Add New" → "Project"
4. Import your GitHub repository

### 2. Configure Project Settings

- **Framework Preset**: Other
- **Root Directory**: `.` (leave default)
- **Build Command**: Leave empty
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

### 3. Environment Variables (Optional)

Set these in Vercel dashboard if needed:
- `SECRET_KEY`: Your Flask secret key
- `LOGO_DEV_API_KEY`: Logo.dev API key (optional, has default)

### 4. Deploy

Click "Deploy" and Vercel will:
1. Install dependencies from `requirements.txt`
2. Build the serverless function
3. Deploy to a URL like `https://your-app-name.vercel.app`

## Features Optimized for Vercel

### 🗄️ Database Management
- Uses `/tmp` directory for SQLite in production
- Automatically creates database from CSV files
- Falls back to sample data if CSV files unavailable
- Separate portfolio database handling

### 🖼️ Logo System
- No local logo storage required
- Uses Clearbit + Logo.dev APIs
- Automatic fallbacks to generated initials
- Perfect for serverless deployment

### ⚡ Performance Optimizations
- Lazy loading for images
- CDN-delivered static assets
- Optimized import structure
- Environment-aware configuration

### 🔧 Error Handling
- Graceful degradation for missing dependencies
- Database recreation on cold starts
- API fallbacks for external services
- Production-ready error pages

## Testing Deployment

After deployment, test these features:
1. **Home Page**: Company cards with logos load
2. **Search**: Autocomplete works with logo display
3. **Predictions**: Stock prediction functionality
4. **Simulator**: Portfolio management and trading
5. **API Endpoints**: `/api/companies` returns data

## Troubleshooting

### Common Issues

1. **Import Errors**: Check `requirements.txt` for missing packages
2. **Database Errors**: Ensure CSV files are in `/static/` directory
3. **Static Files**: Verify paths use `/static/` prefix
4. **Cold Starts**: First request may be slow as database initializes

### Logs

Check Vercel function logs in the dashboard:
- Go to your project → "Functions" tab
- Click on `api/index.py` to see logs
- Monitor for any errors during requests

## Environment Differences

### Development
- Uses local SQLite files
- Debug mode enabled
- Detailed error messages

### Production (Vercel)
- Uses `/tmp` for database storage
- Production optimizations
- Graceful error handling
- HTTPS enforcement

## Post-Deployment

1. **Custom Domain**: Add your domain in Vercel settings
2. **Analytics**: Enable Vercel Analytics if desired
3. **Environment Variables**: Add any production secrets
4. **Monitoring**: Set up error tracking if needed

Your stock prediction app is now ready for production use! 🚀