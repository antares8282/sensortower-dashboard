"""
One-time script: Convert existing data/processed/*.json into dashboard_data/ format.
Also used as a library by data_refresh.py for recomputation.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

DATA_DIR = PROJECT_ROOT / "dashboard_data"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CATEGORIES = {
    "6014": "Games",
    "6015": "Finance",
    "6005": "Social Networking",
    "6007": "Productivity",
    "6008": "Photo & Video",
}

CATEGORY_ID_TO_NAME = {int(k): v for k, v in CATEGORIES.items()}


def get_revenue(app):
    r = app.get("humanized_worldwide_last_month_revenue")
    if isinstance(r, dict):
        return r.get("revenue", 0) or 0
    return 0


def get_downloads(app):
    d = app.get("humanized_worldwide_last_month_downloads")
    if isinstance(d, dict):
        return d.get("downloads", 0) or 0
    return 0


def load_existing_data():
    """Load existing processed data files."""
    free_file = sorted(PROCESSED_DIR.glob("initial_collection_*.json"))
    grossing_file = sorted(PROCESSED_DIR.glob("top_grossing_*.json"))

    free_data = {}
    grossing_data = {}

    if free_file:
        with open(free_file[-1]) as f:
            free_data = json.load(f)
    if grossing_file:
        with open(grossing_file[-1]) as f:
            grossing_data = json.load(f)

    return free_data, grossing_data


def build_rankings(free_data, grossing_data):
    """Build rankings.json: category → chart_type → ranked list with basic info."""
    rankings = {}

    for cat_name in CATEGORIES.values():
        rankings[cat_name] = {}

        if cat_name in free_data and "top_free" in free_data[cat_name]:
            src = free_data[cat_name]["top_free"]
            ranked = []
            app_ids = src.get("ranking", [])
            apps_by_id = {a["app_id"]: a for a in src.get("apps", [])}
            for rank, aid in enumerate(app_ids[:20], 1):
                app = apps_by_id.get(aid, {})
                ranked.append({
                    "rank": rank,
                    "app_id": aid,
                    "name": app.get("name", "Unknown"),
                    "publisher_name": app.get("publisher_name", "Unknown"),
                    "icon_url": app.get("icon_url", ""),
                    "rating": app.get("rating", 0),
                    "revenue": get_revenue(app),
                    "downloads": get_downloads(app),
                    "has_iap": bool(app.get("in_app_purchases")),
                    "price": app.get("price", 0),
                })
            rankings[cat_name]["topfreeapplications"] = {
                "date": src.get("date", ""),
                "country": src.get("country", "US"),
                "apps": ranked,
            }

        if cat_name in grossing_data and "top_grossing" in grossing_data[cat_name]:
            src = grossing_data[cat_name]["top_grossing"]
            ranked = []
            app_ids = src.get("ranking", [])
            apps_by_id = {a["app_id"]: a for a in src.get("apps", [])}
            for rank, aid in enumerate(app_ids[:20], 1):
                app = apps_by_id.get(aid, {})
                ranked.append({
                    "rank": rank,
                    "app_id": aid,
                    "name": app.get("name", "Unknown"),
                    "publisher_name": app.get("publisher_name", "Unknown"),
                    "icon_url": app.get("icon_url", ""),
                    "rating": app.get("rating", 0),
                    "revenue": get_revenue(app),
                    "downloads": get_downloads(app),
                    "has_iap": bool(app.get("in_app_purchases")),
                    "price": app.get("price", 0),
                })
            rankings[cat_name]["topgrossingapplications"] = {
                "date": src.get("date", ""),
                "country": src.get("country", "US"),
                "apps": ranked,
            }

    return rankings


def build_app_details(free_data, grossing_data):
    """Build app_details.json: deduplicated full app records."""
    apps = {}

    for cat_name in CATEGORIES.values():
        for src_key, src_data in [("top_free", free_data), ("top_grossing", grossing_data)]:
            if cat_name not in src_data:
                continue
            chart_data = src_data[cat_name].get(src_key, {})
            for app in chart_data.get("apps", []):
                aid = app["app_id"]
                if aid not in apps:
                    # Extract the fields we care about for the dashboard
                    apps[aid] = {
                        "app_id": aid,
                        "name": app.get("name", ""),
                        "publisher_name": app.get("publisher_name", ""),
                        "publisher_id": app.get("publisher_id"),
                        "icon_url": app.get("icon_url", ""),
                        "url": app.get("url", ""),
                        "os": app.get("os", "ios"),
                        "categories": app.get("categories", []),
                        "category_names": [
                            CATEGORY_ID_TO_NAME.get(c, f"Cat {c}")
                            for c in app.get("categories", [])
                        ],
                        "rating": app.get("rating", 0),
                        "global_rating_count": app.get("global_rating_count", 0),
                        "rating_count": app.get("rating_count", 0),
                        "price": app.get("price", 0),
                        "in_app_purchases": bool(app.get("in_app_purchases")),
                        "revenue": get_revenue(app),
                        "downloads": get_downloads(app),
                        "revenue_string": (app.get("humanized_worldwide_last_month_revenue") or {}).get("string", "N/A"),
                        "downloads_string": (app.get("humanized_worldwide_last_month_downloads") or {}).get("string", "N/A"),
                        "release_date": app.get("release_date", ""),
                        "updated_date": app.get("updated_date", ""),
                        "version": app.get("version", ""),
                        "content_rating": app.get("content_rating", ""),
                        "subtitle": app.get("subtitle", ""),
                        "description": (app.get("description", "") or "")[:500],
                        "screenshot_urls": (app.get("screenshot_urls") or [])[:5],
                        "top_countries": app.get("top_countries", []),
                        "supported_languages": app.get("supported_languages", []),
                        "bundle_id": app.get("bundle_id", ""),
                    }

    return apps


def build_category_summary(rankings, app_details):
    """Build category_summary.json: aggregated KPIs per category."""
    summary = {}

    for cat_name in CATEGORIES.values():
        cat_data = rankings.get(cat_name, {})
        all_app_ids = set()
        total_revenue = 0
        total_downloads = 0
        ratings = []

        for chart_type, chart_data in cat_data.items():
            for app_entry in chart_data.get("apps", []):
                aid = app_entry["app_id"]
                if aid not in all_app_ids:
                    all_app_ids.add(aid)
                    total_revenue += app_entry.get("revenue", 0)
                    total_downloads += app_entry.get("downloads", 0)
                    if app_entry.get("rating", 0) > 0:
                        ratings.append(app_entry["rating"])

        # Top grossing specific metrics
        grossing_apps = cat_data.get("topgrossingapplications", {}).get("apps", [])
        grossing_revenue = sum(a.get("revenue", 0) for a in grossing_apps)
        grossing_downloads = sum(a.get("downloads", 0) for a in grossing_apps)

        summary[cat_name] = {
            "category_id": [k for k, v in CATEGORIES.items() if v == cat_name][0],
            "total_apps_tracked": len(all_app_ids),
            "total_revenue": total_revenue,
            "total_downloads": total_downloads,
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "grossing_revenue": grossing_revenue,
            "grossing_downloads": grossing_downloads,
            "revenue_per_download": round(grossing_revenue / grossing_downloads, 2) if grossing_downloads else 0,
            "top_free_count": len(cat_data.get("topfreeapplications", {}).get("apps", [])),
            "top_grossing_count": len(cat_data.get("topgrossingapplications", {}).get("apps", [])),
        }

    return summary


def build_publisher_summary(app_details, rankings):
    """Build publisher_summary.json: aggregated KPIs per publisher."""
    publisher_apps = defaultdict(list)
    publisher_chart_count = Counter()

    # Count chart appearances
    for cat_name, cat_data in rankings.items():
        for chart_type, chart_data in cat_data.items():
            for app_entry in chart_data.get("apps", []):
                pub = app_entry.get("publisher_name", "Unknown")
                publisher_chart_count[pub] += 1

    # Group apps by publisher
    for aid, app in app_details.items():
        publisher_apps[app["publisher_name"]].append(app)

    summary = []
    for pub_name, apps in publisher_apps.items():
        total_rev = sum(a.get("revenue", 0) for a in apps)
        total_dl = sum(a.get("downloads", 0) for a in apps)
        cats = set()
        for a in apps:
            for cn in a.get("category_names", []):
                cats.add(cn)

        top_app = max(apps, key=lambda x: x.get("revenue", 0))

        summary.append({
            "publisher_name": pub_name,
            "app_count": len(apps),
            "chart_appearances": publisher_chart_count.get(pub_name, 0),
            "total_revenue": total_rev,
            "total_downloads": total_dl,
            "avg_rating": round(
                sum(a.get("rating", 0) for a in apps if a.get("rating", 0) > 0) /
                max(sum(1 for a in apps if a.get("rating", 0) > 0), 1),
                2
            ),
            "categories": sorted(cats),
            "top_app_name": top_app.get("name", ""),
            "top_app_revenue": top_app.get("revenue", 0),
        })

    summary.sort(key=lambda x: -x["chart_appearances"])
    return summary


def build_daily_snapshot(rankings, date_str):
    """Build a compact daily snapshot for historical tracking."""
    snapshot = {
        "date": date_str,
        "categories": {},
    }

    for cat_name, cat_data in rankings.items():
        snapshot["categories"][cat_name] = {}
        for chart_type, chart_data in cat_data.items():
            snapshot["categories"][cat_name][chart_type] = [
                {
                    "rank": a["rank"],
                    "app_id": a["app_id"],
                    "name": a["name"],
                    "revenue": a.get("revenue", 0),
                    "downloads": a.get("downloads", 0),
                }
                for a in chart_data.get("apps", [])
            ]

    return snapshot


def build_trends(snapshots_dir):
    """Build trends.json from all historical snapshots."""
    snapshots = []
    for f in sorted(snapshots_dir.glob("*.json")):
        with open(f) as fh:
            snapshots.append(json.load(fh))

    if not snapshots:
        return {"dates": [], "categories": {}}

    trends = {
        "dates": [s["date"] for s in snapshots],
        "categories": {},
    }

    for cat_name in CATEGORIES.values():
        trends["categories"][cat_name] = {
            "grossing_revenue": [],
            "grossing_downloads": [],
            "free_downloads": [],
        }

        for s in snapshots:
            cat_data = s.get("categories", {}).get(cat_name, {})

            grossing = cat_data.get("topgrossingapplications", [])
            free = cat_data.get("topfreeapplications", [])

            trends["categories"][cat_name]["grossing_revenue"].append(
                sum(a.get("revenue", 0) for a in grossing)
            )
            trends["categories"][cat_name]["grossing_downloads"].append(
                sum(a.get("downloads", 0) for a in grossing)
            )
            trends["categories"][cat_name]["free_downloads"].append(
                sum(a.get("downloads", 0) for a in free)
            )

    return trends


def generate_all():
    """Main function: generate all dashboard data from existing processed files."""
    print("Loading existing data...")
    free_data, grossing_data = load_existing_data()

    if not free_data and not grossing_data:
        print("ERROR: No processed data found in data/processed/")
        return

    print("Building rankings...")
    rankings = build_rankings(free_data, grossing_data)

    print("Building app details...")
    app_details = build_app_details(free_data, grossing_data)

    print("Building category summary...")
    cat_summary = build_category_summary(rankings, app_details)

    print("Building publisher summary...")
    pub_summary = build_publisher_summary(app_details, rankings)

    # Save current data
    current_dir = DATA_DIR / "current"
    current_dir.mkdir(parents=True, exist_ok=True)

    with open(current_dir / "rankings.json", "w") as f:
        json.dump(rankings, f, indent=2)
    print(f"  Wrote rankings.json ({len(rankings)} categories)")

    with open(current_dir / "app_details.json", "w") as f:
        json.dump(app_details, f, indent=2, default=str)
    print(f"  Wrote app_details.json ({len(app_details)} apps)")

    with open(current_dir / "category_summary.json", "w") as f:
        json.dump(cat_summary, f, indent=2)
    print(f"  Wrote category_summary.json")

    with open(current_dir / "publisher_summary.json", "w") as f:
        json.dump(pub_summary, f, indent=2)
    print(f"  Wrote publisher_summary.json ({len(pub_summary)} publishers)")

    # Save historical snapshot
    today = datetime.now().strftime("%Y-%m-%d")
    snapshots_dir = DATA_DIR / "historical" / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    snapshot = build_daily_snapshot(rankings, today)
    with open(snapshots_dir / f"{today}.json", "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"  Wrote snapshot {today}.json")

    # Build trends
    trends = build_trends(snapshots_dir)
    with open(DATA_DIR / "historical" / "trends.json", "w") as f:
        json.dump(trends, f, indent=2)
    print(f"  Wrote trends.json ({len(trends['dates'])} data points)")

    # Metadata
    metadata = {
        "last_refresh": datetime.now().isoformat(),
        "total_apps": len(app_details),
        "categories": list(CATEGORIES.values()),
        "data_source": "SensorTower API",
        "country": "US",
        "platform": "iOS",
    }
    with open(DATA_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Wrote metadata.json")

    print(f"\nDone! Dashboard data ready in {DATA_DIR}/")


if __name__ == "__main__":
    generate_all()
