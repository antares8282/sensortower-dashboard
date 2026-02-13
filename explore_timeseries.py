"""
Explore SensorTower /v1/apps/timeseries endpoint.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('SENSORTOWER_API_TOKEN')
BASE_URL = "https://api.sensortower.com/v1"

TEST_APP_IOS = "553834731"  # Candy Crush iOS

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

def test_timeseries(params):
    """Test timeseries endpoint."""
    url = f"{BASE_URL}/apps/timeseries"
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"\nStatus: {response.status_code}")
        print(f"Params: {json.dumps(params, indent=2)}")

        if response.status_code == 200:
            data = response.json()
            metric = params.get('timeseries', 'unknown').split(',')[0]
            filename = f"timeseries_{metric}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Success! Saved to: {filename}")
            print(f"  Keys: {list(data.keys())[:5]}")
            if isinstance(data, list) and len(data) > 0:
                print(f"  First item keys: {list(data[0].keys())}")
            return data
        else:
            print(f"✗ Error {response.status_code}: {response.text[:400]}")
            return None
    except Exception as e:
        print(f"✗ Exception: {e}")
        return None

print("Testing /v1/apps/timeseries API")
print("="*80)

# Base params
base_params = {
    "app_ids": TEST_APP_IOS,
    "start_date": "2026-01-01",
    "end_date": "2026-01-31",
    "regions": "US",
    "breakdown": "app_id",
}

# Test different timeseries metrics
timeseries_options = [
    # Reviews/Ratings related
    "rating,review_count",
    "rating_breakdown",
    "reviews",

    # Monetization
    "iap_revenue,iap_purchases",
    "revenue,downloads",

    # Engagement
    "time_spent,session_count,session_duration",

    # Store metrics
    "downloads,revenue,rating",
]

for ts in timeseries_options:
    print(f"\n{'='*80}")
    print(f"### Timeseries: {ts}")
    params = {**base_params, "timeseries": ts}
    test_timeseries(params)

print("\n" + "="*80)
print("Exploration complete!")
print("="*80)
