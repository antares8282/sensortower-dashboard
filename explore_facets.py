"""
Explore SensorTower Facets API (the one shown in the screenshot).
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('SENSORTOWER_API_TOKEN')
BASE_URL = "https://api.sensortower.com/v1"

TEST_APP_IOS = "553834731"  # Candy Crush

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

def test_facet(params):
    """Test facets/metrics endpoint."""
    url = f"{BASE_URL}/facets/metrics"
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"\nStatus: {response.status_code}")
        print(f"Params: {params}")

        if response.status_code == 200:
            data = response.json()
            filename = f"facet_test_{params.get('bundle', 'unknown')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Success! Saved to: {filename}")
            print(f"  Keys: {list(data.keys())}")
            return data
        else:
            print(f"✗ Error: {response.text[:300]}")
            return None
    except Exception as e:
        print(f"✗ Exception: {e}")
        return None

print("Testing Facets API")
print("="*80)

# Try different bundles based on screenshot examples
bundles = [
    "app_overview",
    "retention_daily",
    "demographics",
    "session_metrics",
    "engagement",
    "app_updates",
    "iap_revenue",
    "monetization",
    "reviews",
    "ratings"
]

for bundle in bundles:
    print(f"\n### Bundle: {bundle}")
    test_facet({
        "bundle": bundle,
        "app_ids": TEST_APP_IOS,
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "regions": "US"
    })

print("\n" + "="*80)
print("Exploration complete!")
