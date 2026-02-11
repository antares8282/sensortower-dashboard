# Claude Instructions for SensorTower Market Analysis Project

## Project Overview

This is a data analysis project that uses the SensorTower API to identify mobile app market trends and analyze successful apps. The **critical constraint** is a monthly API limit of 2,000-3,000 requests, requiring aggressive caching and smart request strategies.

## Core Principles

### 1. API Conservation is CRITICAL
- **ALWAYS check cache first** before making any API request
- **NEVER make unnecessary API calls** - every request counts toward our 2-3k monthly limit
- Use `python check_usage.py` to verify current usage before batch operations
- Default cache TTL is 168 hours (1 week) - extend this for historical data
- Warn the user if monthly usage exceeds 1,500 requests

### 2. Project Structure
```
data/
  raw/cache/          # Cached API responses (DO NOT delete)
  processed/          # Analysis outputs
  api_usage_log.json  # Tracks every API call
src/
  api/                # SensorTowerClient with smart caching
  analysis/           # TrendAnalyzer and analysis tools
  utils/              # Helper functions
notebooks/            # Jupyter notebooks for exploration
config/               # Category definitions and configs
```

### 3. Key Files
- `src/api/sensortower_client.py` - Main API client with caching
- `src/analysis/trend_analyzer.py` - Analysis tools
- `check_usage.py` - Monitor API usage (run this often!)
- `test_endpoints.py` - Find correct API endpoints
- `.env` - Contains `SENSORTOWER_API_TOKEN`

## Common Tasks

### Before ANY API Work
```bash
# ALWAYS check usage first
python check_usage.py
```

### Making API Requests
```python
from src.api.sensortower_client import SensorTowerClient

# Initialize with long cache time
client = SensorTowerClient(cache_ttl_hours=168)

# Check usage FIRST
current_usage = client.get_monthly_usage()
print(f"Current usage: {current_usage}/2500")

# Make request (uses cache if available)
data = client.get_top_apps(
    country="US",
    device="ios",
    chart="topgrossing",
    limit=20,
    use_cache=True  # ALWAYS True unless explicitly updating
)
```

### Data Analysis (No API Calls)
```python
from src.analysis.trend_analyzer import TrendAnalyzer

analyzer = TrendAnalyzer()

# All analysis uses cached/processed data
category_perf = analyzer.analyze_category_performance(apps_data)
patterns = analyzer.analyze_successful_app_patterns(top_apps)
report = analyzer.generate_insights_report(apps_data)
```

### Finding Correct Endpoints
```bash
# SensorTower endpoints vary by subscription
python test_endpoints.py
```

## Critical Rules for Claude

### ✅ DO
1. **Check API usage** before any batch operations
2. **Use cached data** whenever possible
3. **Extend cache TTL** for historical data (use 720 hours / 30 days)
4. **Batch requests** efficiently (collect multiple categories in one session)
5. **Save processed data** to avoid re-fetching
6. **Monitor usage** with `check_usage.py` regularly
7. **Use Jupyter notebooks** for exploratory analysis

### ❌ DON'T
1. **Never disable caching** (`use_cache=False`) without explicit user request
2. **Never make redundant API calls** - check if data exists first
3. **Never delete** `data/raw/cache/` or `api_usage_log.json`
4. **Never fetch** all categories or large datasets without planning
5. **Don't ignore** usage warnings in the output

## API Usage Budget Guidance

### Monthly Allocation (2,500 request budget)
- **Initial data collection**: ~100 requests
  - Top 20 apps × 5 key categories = 5 requests
  - App details for top 50 = 50 requests
  - Category metadata = ~10 requests

- **Weekly monitoring**: ~20 requests/week × 4 = 80 requests
  - Update top charts = ~5 requests
  - Track specific apps = ~10 requests

- **Deep dives**: ~50 requests/month
  - New category exploration
  - Competitive analysis

- **Reserve**: ~2,270 requests
  - Emergency use only
  - Large one-time analyses with user approval

### Usage Alert Thresholds
- **1,500+ requests**: Warn user, suggest reviewing necessity
- **2,000+ requests**: Strong warning, require explicit confirmation
- **2,500+ requests**: Critical - should avoid all non-essential calls

## Data Collection Strategy

### Phase 1: Initial Collection (5-10 API calls)
```python
# Focus on high-value categories only
focus_categories = {
    "6014": "Games",
    "6015": "Finance",
    "6005": "Social Networking",
    "6007": "Productivity",
    "6008": "Photo & Video"
}

# Collect top 20 from each (5 API calls total)
for cat_id, name in focus_categories.items():
    data = client.get_top_apps(category=cat_id, limit=20, use_cache=True)
    # Cache stores this for 1 week
```

### Phase 2: Analysis (0 API calls)
```python
# Use cached data for all analysis
analyzer = TrendAnalyzer()
insights = analyzer.analyze_category_performance(cached_data)
patterns = analyzer.analyze_successful_app_patterns(cached_data)
```

### Phase 3: Updates (Minimal calls)
```python
# Only refresh specific high-priority data
client.get_top_apps(category="6014", limit=10, use_cache=False)  # 1 call
```

## Working with Notebooks

The `notebooks/01_initial_exploration.ipynb` is set up for:
- Collecting initial data efficiently
- Performing exploratory analysis
- Visualizing trends
- Tracking API usage within the notebook

**Always run the usage check cell first!**

## Error Handling

### Common Issues

1. **404 Not Found**
   - Endpoint URL is incorrect for the subscription
   - Run `python test_endpoints.py` to find correct endpoints
   - Update `BASE_URL` in `sensortower_client.py`

2. **401 Unauthorized**
   - API token is invalid or expired
   - Check `.env` file has correct `SENSORTOWER_API_TOKEN`
   - Verify token with SensorTower support

3. **403 Forbidden**
   - Endpoint not included in subscription plan
   - Try alternative endpoints
   - Contact SensorTower about access

4. **Rate Limiting**
   - Built-in delays should prevent this
   - Increase `rate_limit_delay` if needed
   - Check if caching is working properly

## Analysis Capabilities

### Built-in Analysis Functions
- `analyze_category_performance()` - Compare categories
- `identify_emerging_trends()` - Spot rising patterns
- `analyze_successful_app_patterns()` - Success factors
- `compare_competitors()` - Competitive analysis
- `generate_insights_report()` - Automated markdown reports

### Custom Analysis
Add new analysis functions to `src/analysis/trend_analyzer.py`

Keep them **data-focused** (no API calls within analysis functions)

## File Naming Conventions

### Processed Data
```
data/processed/top_apps_{timestamp}.csv
data/processed/category_analysis_{date}.xlsx
data/processed/trends_report_{date}.json
```

### Reports
```
reports/market_insights_{date}.md
reports/competitor_analysis_{apps}_{date}.pdf
```

### Cache Files
```
data/raw/cache/{md5_hash}.json  # Auto-generated by client
```

## Code Style

### Imports
```python
# Standard library
import os
import json
from datetime import datetime
from pathlib import Path

# Third-party
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Local
from src.api.sensortower_client import SensorTowerClient
from src.analysis.trend_analyzer import TrendAnalyzer
```

### API Client Usage Pattern
```python
# Always initialize with usage check
client = SensorTowerClient(cache_ttl_hours=168)
print(f"Current usage: {client.get_monthly_usage()}")

# Make requests with caching
data = client.get_top_apps(..., use_cache=True)

# Save processed results
df = pd.DataFrame(data)
df.to_csv(f"data/processed/output_{datetime.now():%Y%m%d}.csv")
```

## Dependencies

Core packages in `requirements.txt`:
- `requests` - API calls
- `python-dotenv` - Environment variables
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `matplotlib`, `seaborn`, `plotly` - Visualization
- `jupyter` - Notebooks
- `openpyxl` - Excel export

## Testing New Features

1. Create test script in project root
2. Use small data samples (limit=5)
3. Verify caching works
4. Check usage after testing
5. Move to `src/` when stable

## Maintenance Tasks

### Weekly
- Run `python check_usage.py`
- Review cache size: `du -sh data/raw/cache`
- Check for new trends in data

### Monthly
- Clear old cache: `client.clear_old_cache(days=30)`
- Review usage patterns
- Update analysis notebooks

## User Interaction Guidelines

### When User Asks for Data Collection
1. **Check current usage first**
2. **Estimate API calls needed**
3. **Present the plan** with call count
4. **Get user approval** if > 10 calls
5. **Execute** with progress updates
6. **Report** final usage after completion

### Example Response
```
I'll collect top 20 apps from 5 categories.

Estimated API calls: 5
Current monthly usage: 127/2500
After operation: ~132/2500 (5.3%)

Proceeding...
[Execute with progress updates]

✓ Complete!
- Collected 100 apps
- Used 5 API calls
- All data cached for 7 days
- New monthly total: 132/2500
```

## Quick Reference

```bash
# Check API usage
python check_usage.py

# Test API endpoints
python test_endpoints.py

# Quick start test
python quickstart.py

# Install dependencies
pip install -r requirements.txt

# Start Jupyter
jupyter notebook notebooks/
```

## Goals & Success Metrics

### Primary Goals
1. **Stay under API limit** - Monitor constantly
2. **Identify 3-5 market trends** - Emerging categories, monetization patterns
3. **Analyze top performers** - What makes them successful
4. **Generate actionable insights** - Reports for decision-making

### Success Metrics
- API usage < 2,000/month
- 90%+ cache hit rate on repeated queries
- Weekly trend reports generated
- Competitive analysis dashboard created

## Remember

**Every API call counts. Cache everything. Analyze smartly.**

The caching system is your best friend - use it aggressively to stay within limits while getting comprehensive insights.
