"""
Explore SensorTower API endpoints for additional app data.
Focus: Rating breakdowns, IAP packages, detailed reviews.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('SENSORTOWER_API_TOKEN')
BASE_URL = "https://api.sensortower.com/v1"

# Test app: Candy Crush (popular, likely has IAPs and reviews)
TEST_APP_IOS = "553834731"  # Candy Crush Saga iOS
TEST_APP_ANDROID = "com.king.candycrushsaga"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

def test_endpoint(endpoint, params=None):
    """Test an endpoint and return response data."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"\n{'='*80}")
        print(f"Endpoint: {endpoint}")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")

            # Save to file for inspection
            filename = f"endpoint_test_{endpoint.replace('/', '_')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved to: {filename}")

            # Show sample data structure
            if isinstance(data, dict):
                for key, value in list(data.items())[:3]:
                    if isinstance(value, (dict, list)):
                        print(f"  {key}: {type(value).__name__} (len: {len(value)})")
                    else:
                        print(f"  {key}: {value}")

            return data
        else:
            print(f"Error: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"Exception: {e}")
        return None

print("Testing SensorTower API Endpoints")
print("="*80)

# 1. Test app details (baseline - we know this works)
print("\n\n### 1. BASELINE: App Details (known working)")
test_endpoint("ios/apps", {"app_ids": TEST_APP_IOS})

# 2. Test app reviews endpoint (if exists)
print("\n\n### 2. REVIEWS: Try reviews endpoint")
test_endpoint("ios/reviews", {"app_id": TEST_APP_IOS})
test_endpoint(f"ios/apps/{TEST_APP_IOS}/reviews", {})

# 3. Test rating breakdown
print("\n\n### 3. RATINGS: Try rating breakdown")
test_endpoint("ios/ratings", {"app_id": TEST_APP_IOS})
test_endpoint(f"ios/apps/{TEST_APP_IOS}/ratings", {})

# 4. Test IAP/monetization endpoints
print("\n\n### 4. IAP: Try in-app purchase endpoints")
test_endpoint("ios/iap", {"app_id": TEST_APP_IOS})
test_endpoint(f"ios/apps/{TEST_APP_IOS}/iap", {})
test_endpoint("ios/monetization", {"app_id": TEST_APP_IOS})
test_endpoint(f"ios/apps/{TEST_APP_IOS}/monetization", {})

# 5. Test app overview (might have extended metadata)
print("\n\n### 5. OVERVIEW: Try app overview")
test_endpoint("ios/overview", {"app_id": TEST_APP_IOS})
test_endpoint(f"ios/apps/{TEST_APP_IOS}/overview", {})

# 6. Test store data (might have IAP info)
print("\n\n### 6. STORE: Try store data")
test_endpoint("ios/store", {"app_id": TEST_APP_IOS})
test_endpoint(f"ios/apps/{TEST_APP_IOS}/store", {})

# 7. Test unified app endpoint (might have more fields)
print("\n\n### 7. UNIFIED: Try unified app data")
test_endpoint("unified/apps", {"app_ids": TEST_APP_IOS, "app_id_type": "itunes"})

print("\n\n" + "="*80)
print("Exploration complete! Check generated JSON files for details.")
print("="*80)
