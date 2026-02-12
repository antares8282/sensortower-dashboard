"""
Daily data refresh script.
Run via GitHub Actions or manually: python scripts/data_refresh.py

Fetches fresh data from SensorTower API, updates dashboard_data/.
Cost: ~100 API calls per run (23 categories × 2 chart types × 2 calls + sales estimates).
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

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
    build_all_apps_table,
    build_category_summary,
    build_publisher_summary,
    build_daily_snapshot,
    build_trends,
    get_revenue,
    get_downloads,
)


def fetch_sales_estimates(client, app_ids_list):
    """Fetch sales estimates for 1m, 3m, 6m periods.

    Returns dict keyed by app_id → {downloads_1m, revenue_1m, downloads_3m, ...}
    """
    today = datetime.now()
    periods = {
        "1m": (today - timedelta(days=30), today),
        "3m": (today - timedelta(days=90), today),
        "6m": (today - timedelta(days=180), today),
    }

    # Initialize results
    results = defaultdict(lambda: {
        "downloads_1m": 0, "revenue_1m": 0,
        "downloads_3m": 0, "revenue_3m": 0,
        "downloads_6m": 0, "revenue_6m": 0,
    })

    # Batch app_ids in groups of 100
    batches = []
    for i in range(0, len(app_ids_list), 100):
        batches.append(app_ids_list[i:i + 100])

    for period_key, (start_dt, end_dt) in periods.items():
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")
        dl_key = f"downloads_{period_key}"
        rev_key = f"revenue_{period_key}"

        for batch_idx, batch in enumerate(batches):
            print(f"  Sales estimates {period_key} batch {batch_idx + 1}/{len(batches)} ({len(batch)} apps)...")
            try:
                data = client.get_sales_estimates(
                    app_ids=batch,
                    device="ios",
                    date_granularity="monthly",
                    start_date=start_str,
                    end_date=end_str,
                    use_cache=True,  # Cache sales estimates
                )
                if isinstance(data, list):
                    for record in data:
                        aid = record.get("aid")
                        if aid:
                            results[aid][dl_key] += record.get("iu", 0) or 0
                            results[aid][rev_key] += int((record.get("ir", 0) or 0) / 100)
                elif isinstance(data, dict):
                    # Some responses wrap in a dict
                    for record in data.get("data", data.get("estimates", [])):
                        aid = record.get("aid")
                        if aid:
                            results[aid][dl_key] += record.get("iu", 0) or 0
                            results[aid][rev_key] += int((record.get("ir", 0) or 0) / 100)
            except Exception as e:
                print(f"    WARNING: Sales estimates failed for {period_key} batch {batch_idx + 1}: {e}")

    return dict(results)


def refresh_data():
    """Fetch fresh data from API and rebuild dashboard data."""
    client = SensorTowerClient(cache_ttl_hours=12)  # Short TTL for refresh

    usage_before = client.get_monthly_usage()
    print(f"API usage before refresh: {usage_before}/2500")

    if usage_before >= 2000:
        print("WARNING: Monthly usage is high! Consider skipping refresh.")

    today = datetime.now().strftime("%Y-%m-%d")
    # Use yesterday for rankings (today's data may not be available yet)
    ranking_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Using ranking date: {ranking_date}")

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
            date=ranking_date,
            limit=50,
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
            date=ranking_date,
            limit=50,
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

    # Collect all unique app_ids for sales estimates
    all_app_ids = list({int(aid) for aid in app_details.keys()})
    print(f"\nFetching sales estimates for {len(all_app_ids)} unique apps...")
    sales_estimates = fetch_sales_estimates(client, all_app_ids)
    print(f"  Got estimates for {len(sales_estimates)} apps")

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

    all_apps_table = build_all_apps_table(rankings, app_details, sales_estimates)
    with open(current_dir / "all_apps_table.json", "w") as f:
        json.dump(all_apps_table, f, indent=2, default=str)

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
