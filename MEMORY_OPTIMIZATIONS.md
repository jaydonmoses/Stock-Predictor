# Deploy to Render Free Tier with Memory Optimizations

## Key Optimizations Made:

### 1. **Removed Heavy Dependencies**
- Removed **Plotly** (large JavaScript library)
- Removed **SHAP** (memory-intensive explainability library)
- Replaced with lightweight alternatives

### 2. **Memory-Optimized Data Processing**
- Reduced data download period from 5+ years to 1 year
- Limited model complexity (50 trees vs 100, max depth 10)
- Chunked database operations
- Immediate memory cleanup with `gc.collect()`
- Limited test/prediction data to recent samples only

### 3. **Database Optimizations**
- Added error handling for CSV file operations
- Chunked CSV reading for large files
- Used context managers for database connections
- Reduced query result limits

### 4. **Model Optimizations**
- Simplified feature set (removed SMA_20, kept essential indicators)
- Single model training (removed duplicate training)
- Simple feature importance without SHAP
- Limited prediction history to 20 samples

### 5. **Web App Optimizations**
- Memory cleanup after each request
- Reduced API response limits (100 companies max)
- Replaced Plotly with Chart.js (lighter alternative)
- Added garbage collection in critical paths

### 6. **Server Configuration**
- Optimized Gunicorn settings for free tier:
  - Single worker to reduce memory
  - 2 threads for concurrency
  - Worker temp directory in shared memory
  - Request limits to prevent memory leaks
  - Preload app for efficiency

## Expected Memory Usage:
- **Before**: ~800MB-1.2GB (would exceed free tier limit)
- **After**: ~300-500MB (within Render free tier 512MB limit)

## Deploy to Render:
1. Push these changes to GitHub
2. Connect your Render account to GitHub
3. Create a new Web Service
4. Use the optimized `render.yaml` configuration
5. Deploy!

The app should now run successfully on Render's free tier with these optimizations.
