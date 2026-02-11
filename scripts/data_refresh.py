"""
Daily data refresh script.
Run via GitHub Actions or manually: python scripts/data_refresh.py

Fetches fresh data from SensorTower API, updates dashboard_data/.
Cost: ~20 API calls per run (5 categories × 2 chart types × 2 calls each).
"""
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from api.sensortower_client import SensorTowerClient, CHART_TOP_FREE, CHART_TOP_GROSSING

# Reuse the dashboard data generation logic
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from generate_dashboard_data import (
    CATEGORIES,
    DATA_DIR,
    build_rankings,
    build_app_details,
    build_category_summary,
    build_publisher_summary,
    build_daily_snapshot,
    build_trends,
    get_revenue,
    get_downloads,
)


def refresh_data():
    """Fetch fresh data from API and rebuild dashboard data."""
    client = SensorTowerClient(cache_ttl_hours=12)  # Short TTL for refresh

    usage_before = client.get_monthly_usage()
    print(f"API usage before refresh: {usage_before}/2500")

    if usage_before >= 2000:
        print("WARNING: Monthly usage is high! Consider skipping refresh.")

    today = datetime.now().strftime("%Y-%m-%d")

    # Collect data in the same format as the initial collection scripts
    free_data = {}
    grossing_data = {}

    for cat_id, cat_name in CATEGORIES.items():
        print(f"\nRefreshing {cat_name}...")

        # Top Free
        result = client.get_top_apps(
            category=cat_id,
            chart_type=CHART_TOP_FREE,
            country="US",
            limit=20,
            resolve_details=True,
            use_cache=False,  # Force fresh data
        )
        free_data[cat_name] = {
            "category_id": cat_id,
            "top_free": result,
        }
        print(f"  Top Free: {len(result.get('apps', []))} apps")

        # Top Grossing
        result = client.get_top_apps(
            category=cat_id,
            chart_type=CHART_TOP_GROSSING,
            country="US",
            limit=20,
            resolve_details=True,
            use_cache=False,
        )
        grossing_data[cat_name] = {
            "category_id": cat_id,
            "top_grossing": result,
        }
        print(f"  Top Grossing: {len(result.get('apps', []))} apps")

    # Rebuild dashboard data
    print("\nRebuilding dashboard data...")

    rankings = build_rankings(free_data, grossing_data)
    app_details = build_app_details(free_data, grossing_data)
    cat_summary = build_category_summary(rankings, app_details)
    pub_summary = build_publisher_summary(app_details, rankings)

    # Save current
    current_dir = DATA_DIR / "current"
    current_dir.mkdir(parents=True, exist_ok=True)

    with open(current_dir / "rankings.json", "w") as f:
        json.dump(rankings, f, indent=2)

    with open(current_dir / "app_details.json", "w") as f:
        json.dump(app_details, f, indent=2, default=str)

    with open(current_dir / "category_summary.json", "w") as f:
        json.dump(cat_summary, f, indent=2)

    with open(current_dir / "publisher_summary.json", "w") as f:
        json.dump(pub_summary, f, indent=2)

    # Save daily snapshot
    snapshots_dir = DATA_DIR / "historical" / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    snapshot = build_daily_snapshot(rankings, today)
    with open(snapshots_dir / f"{today}.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    # Rebuild trends
    trends = build_trends(snapshots_dir)
    with open(DATA_DIR / "historical" / "trends.json", "w") as f:
        json.dump(trends, f, indent=2)

    # Update metadata
    usage_after = client.get_monthly_usage()
    metadata = {
        "last_refresh": datetime.now().isoformat(),
        "total_apps": len(app_details),
        "categories": list(CATEGORIES.values()),
        "data_source": "SensorTower API",
        "country": "US",
        "platform": "iOS",
        "api_calls_this_refresh": usage_after - usage_before,
        "api_usage_monthly": usage_after,
    }
    with open(DATA_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Also save raw processed data for backup
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    with open(processed_dir / f"initial_collection_{today.replace('-', '')}.json", "w") as f:
        json.dump(free_data, f, indent=2, default=str)

    with open(processed_dir / f"top_grossing_{today.replace('-', '')}.json", "w") as f:
        json.dump(grossing_data, f, indent=2, default=str)

    print(f"\nRefresh complete!")
    print(f"  Apps: {len(app_details)}")
    print(f"  API calls used: {usage_after - usage_before}")
    print(f"  Monthly total: {usage_after}/2500")
    print(f"  Historical snapshots: {len(trends['dates'])}")


if __name__ == "__main__":
    refresh_data()
