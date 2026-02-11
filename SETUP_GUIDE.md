# SensorTower Setup Guide

## ✅ Project Created Successfully!

Your clean slate is ready with a well-structured project focused on market trend analysis.

## 🎯 Project Goals

1. **Minimize API Calls**: Stay within 2k-3k monthly limit with aggressive caching
2. **Identify Trends**: Find emerging patterns in app markets
3. **Analyze Success**: Dissect what makes top apps successful

## 📁 Project Structure

```
SensorTower/
├── .env                          # Your API token (already configured)
├── README.md                     # Project overview
├── requirements.txt              # Python dependencies
├── quickstart.py                 # Quick test script
├── check_usage.py               # Monitor API usage
│
├── config/
│   └── categories.json          # App category definitions
│
├── data/
│   ├── raw/cache/              # Cached API responses (saves API calls!)
│   ├── processed/              # Analyzed data
│   └── api_usage_log.json      # Tracks every API request
│
├── src/
│   ├── api/
│   │   └── sensortower_client.py   # Smart API client with caching
│   ├── analysis/
│   │   └── trend_analyzer.py       # Market trend analysis tools
│   └── utils/
│
├── notebooks/
│   └── 01_initial_exploration.ipynb  # Jupyter notebook for exploration
│
└── reports/                     # Generated analysis reports
```

## 🚀 Next Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify API Token

Your token is already in `.env`:
```
SENSORTOWER_API_TOKEN=ST0_nzLhoASd_kJYxFJHXeVxe6N
```

### 3. Find Correct API Endpoints

SensorTower's API endpoints might vary by your subscription plan. You need to:

1. Check SensorTower's API documentation for your account
2. Update the endpoints in `src/api/sensortower_client.py`

Common endpoint patterns:
- `/v1/apps/{app_id}` - App details
- `/v1/rankings` - App rankings
- `/v1/unified` - Unified data endpoints
- `/v1/ios/rankings` - iOS specific rankings

### 4. Test API Connection

Create a simple test script to verify your endpoints:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('SENSORTOWER_API_TOKEN')

# Test different endpoint patterns
endpoints = [
    'https://api.sensortower.com/v1/ios/rankings',
    'https://api.sensortower.com/v1/unified/ios/rankings',
    # Add more based on your docs
]

for endpoint in endpoints:
    response = requests.get(
        endpoint,
        headers={'Authorization': f'Bearer {token}'},
        params={'country': 'US', 'limit': 5}
    )
    print(f"{endpoint}: {response.status_code}")
```

### 5. Update Client Code

Once you find the correct endpoints, update them in:
- `src/api/sensortower_client.py` (BASE_URL and endpoint paths)

## 🎨 Key Features Built-In

### 1. **Smart Caching System**
- Automatically caches all API responses
- Default: 1 week cache (configurable)
- Saves API calls on repeated queries
- Cache stored in `data/raw/cache/`

### 2. **API Usage Tracking**
- Every request logged in `data/api_usage_log.json`
- Monthly usage summaries
- Run `python check_usage.py` anytime to see usage

### 3. **Trend Analysis Tools**
- Category performance analysis
- Success pattern identification
- Competitive comparison
- Automated insights reports

### 4. **Jupyter Notebooks**
- Interactive data exploration
- Visual analytics
- Easy experimentation

## 📊 Recommended Workflow

### Phase 1: Initial Data Collection (Budget: ~100 API calls)
```python
from src.api.sensortower_client import SensorTowerClient

client = SensorTowerClient(cache_ttl_hours=168)

# Collect top 20 apps from 5 key categories
# 5 categories × 1 request = 5 API calls
# Results cached for 1 week!
```

### Phase 2: Deep Analysis (Budget: ~50 API calls)
- Get detailed data for top performers
- All subsequent analysis uses cached data
- Zero additional API calls!

### Phase 3: Ongoing Monitoring (Budget: ~20 calls/week)
- Weekly updates for key metrics
- Cache handles all repeated queries

## 🛡️ Safety Features

1. **Rate Limiting**: Built-in delays between requests
2. **Usage Warnings**: Alerts when approaching limits
3. **Cache-First**: Always checks cache before API
4. **Request Logging**: Track every single API call

## 💡 Best Practices

1. **Always use cache**: Set `use_cache=True` (default)
2. **Long cache times**: Use 168+ hours for historical data
3. **Batch your queries**: Collect multiple categories at once
4. **Check usage regularly**: Run `python check_usage.py`
5. **Focus categories**: Don't try to analyze everything

## 🔍 Analysis Ideas

1. **Revenue Patterns**: Compare monetization across categories
2. **Feature Trends**: Identify common features in top apps
3. **Category Growth**: Track emerging categories
4. **Competitive Gaps**: Find underserved niches
5. **Success Metrics**: Correlate features with performance

## 📞 Need Help?

1. Check SensorTower's official API docs for your plan
2. Update endpoint URLs in the client code
3. Use the Jupyter notebook for exploration
4. Monitor API usage closely

## ⚠️ Important Notes

- **No SensorTower MCP exists** (I searched the registry)
- API endpoints vary by subscription plan
- You'll need to verify the correct endpoints
- The caching system will save you thousands of API calls
- Always check usage before batch operations

---

**You're all set!** The project is clean, organized, and ready for data-driven insights. 🚀
