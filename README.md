# SensorTower Market Trends & App Analysis

A data-driven project to analyze mobile app market trends and dissect successful apps using the SensorTower API.

## Project Goals

1. **Identify Market Trends**: Discover emerging patterns in app categories, monetization, and user engagement
2. **Analyze Successful Apps**: Deep dive into what makes top-performing apps successful
3. **API Efficiency**: Minimize API calls (2k-3k/month limit) through smart caching and batch operations

## Project Structure

```
.
├── data/                    # Cached API responses and processed data
│   ├── raw/                # Raw API responses (cached)
│   └── processed/          # Cleaned and analyzed data
├── src/                    # Source code
│   ├── api/               # API client and request handlers
│   ├── analysis/          # Data analysis modules
│   └── utils/             # Helper functions
├── notebooks/             # Jupyter notebooks for exploration
├── reports/               # Generated analysis reports
└── config/               # Configuration files
```

## API Usage Strategy

To stay within our 2k-3k monthly limit:
- **Cache aggressively**: Store all API responses locally
- **Batch requests**: Group similar queries together
- **Smart sampling**: Focus on representative data sets
- **Incremental updates**: Only fetch new/changed data

## Setup

1. API token is already configured in `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Run initial data collection (carefully!)

## Key Analysis Areas

- Category performance trends
- Revenue model effectiveness
- User acquisition patterns
- Feature correlation with success
- Competitive positioning
