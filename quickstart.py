"""
Quick Start Script
Demonstrates basic usage and tests the API connection
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from api.sensortower_client import SensorTowerClient, CHART_TOP_FREE, CHART_TOP_GROSSING
from analysis.trend_analyzer import TrendAnalyzer


def main():
    print("=" * 60)
    print("SensorTower Market Analysis - Quick Start")
    print("=" * 60)

    # Initialize client with 1-week cache
    print("\n[1] Initializing API client...")
    client = SensorTowerClient(cache_ttl_hours=168)

    current_usage = client.get_monthly_usage()
    print(f"  Current month API usage: {current_usage} requests")

    if current_usage >= 2500:
        print("  WARNING: Approaching monthly limit (2500+)")
    elif current_usage >= 2000:
        print("  CAUTION: Over 2000 requests this month")

    # Test: get top 10 grossing games
    print("\n[2] Fetching top 10 grossing iOS games (US)...")
    print("  (This uses 2 API calls: 1 for rankings + 1 for app details)")
    try:
        result = client.get_top_apps(
            category="6014",
            chart_type=CHART_TOP_GROSSING,
            country="US",
            limit=10,
            resolve_details=True,
            use_cache=True
        )

        apps = result.get("apps", [])
        print(f"\n  Top 10 Grossing Games:")
        print("  " + "-" * 55)
        for i, app in enumerate(apps[:10], 1):
            print(f"  {i:2d}. {app['name']:<40} | {app['publisher_name']}")

    except Exception as e:
        print(f"  Error: {e}")
        print("\n  Troubleshooting:")
        print("  - Run 'python test_endpoints.py' to verify endpoints")
        print("  - Check .env has a valid SENSORTOWER_API_TOKEN")
        return

    # Initialize analyzer
    print("\n[3] Initializing trend analyzer...")
    analyzer = TrendAnalyzer()
    print("  Analyzer ready")

    # Summary
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print(f"\nAPI usage this month: {client.get_monthly_usage()} / 2500")
    print("\nNext steps:")
    print("  1. Collect data: python -m src.api.sensortower_client")
    print("  2. Explore: jupyter notebook notebooks/01_initial_exploration.ipynb")
    print("  3. Monitor: python check_usage.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
