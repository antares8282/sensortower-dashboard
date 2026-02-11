"""
SensorTower API Endpoint Explorer
Use this to find the correct endpoints for your subscription
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('SENSORTOWER_API_TOKEN')
if not API_TOKEN:
    print("ERROR: SENSORTOWER_API_TOKEN not found in .env")
    exit(1)

print("=" * 70)
print("SensorTower API Endpoint Explorer")
print("=" * 70)
print(f"\nAPI Token: {API_TOKEN[:10]}...{API_TOKEN[-5:]}")
print("\nTesting common endpoint patterns...\n")

# Common endpoint patterns to test
test_endpoints = [
    # Rankings endpoints
    {
        "url": "https://api.sensortower.com/v1/rankings",
        "params": {"country": "US", "device": "ios", "limit": 5}
    },
    {
        "url": "https://api.sensortower.com/v1/ios/rankings",
        "params": {"country": "US", "limit": 5}
    },
    {
        "url": "https://api.sensortower.com/v1/unified/ios/rankings",
        "params": {"country": "US", "limit": 5}
    },
    {
        "url": "https://api.sensortower.com/v1/ios/rankings/get_tops",
        "params": {"country": "US", "limit": 5}
    },

    # App info endpoints
    {
        "url": "https://api.sensortower.com/v1/apps",
        "params": {}
    },
    {
        "url": "https://api.sensortower.com/v1/ios/apps",
        "params": {}
    },

    # Categories
    {
        "url": "https://api.sensortower.com/v1/categories",
        "params": {}
    },
    {
        "url": "https://api.sensortower.com/v1/ios/categories",
        "params": {}
    },
]

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

successful_endpoints = []

for i, endpoint in enumerate(test_endpoints, 1):
    url = endpoint["url"]
    params = endpoint["params"]

    print(f"[{i}/{len(test_endpoints)}] Testing: {url}")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        status = response.status_code

        if status == 200:
            print(f"  ✅ SUCCESS (200)")
            print(f"  Response preview: {str(response.json())[:100]}...")
            successful_endpoints.append({
                "url": url,
                "params": params,
                "response_keys": list(response.json().keys()) if isinstance(response.json(), dict) else "list"
            })
        elif status == 401:
            print(f"  ❌ UNAUTHORIZED (401) - Check API token")
        elif status == 404:
            print(f"  ❌ NOT FOUND (404) - Wrong endpoint")
        elif status == 403:
            print(f"  ❌ FORBIDDEN (403) - Not included in your plan")
        else:
            print(f"  ⚠️  Status: {status}")
            if response.text:
                print(f"  Message: {response.text[:100]}")

    except requests.exceptions.Timeout:
        print(f"  ⏱️  TIMEOUT")
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)[:50]}")

    print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)

if successful_endpoints:
    print(f"\n✅ Found {len(successful_endpoints)} working endpoint(s):\n")
    for ep in successful_endpoints:
        print(f"URL: {ep['url']}")
        print(f"Params: {ep['params']}")
        print(f"Response structure: {ep['response_keys']}")
        print()

    print("\n📝 NEXT STEPS:")
    print("1. Update the BASE_URL in src/api/sensortower_client.py")
    print("2. Update the endpoint paths in the client methods")
    print("3. Run quickstart.py again to test")
else:
    print("\n❌ No working endpoints found!")
    print("\n📝 NEXT STEPS:")
    print("1. Check your SensorTower API documentation")
    print("2. Verify your API token is valid and active")
    print("3. Confirm your subscription includes API access")
    print("4. Contact SensorTower support if needed")

print("\n" + "=" * 70)
