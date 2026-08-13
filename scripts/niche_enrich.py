"""
Phase 2b: attach real performance data to the shortlist.

Two batched passes over the shortlisted app_ids (100 per call):
  1. ios/apps                    -> rating, rating_count, price, IAP flag,
                                    supported_languages, last update, subtitle
  2. ios/sales_report_estimates  -> downloads + revenue, TR-only and worldwide,
                                    last 12 months, monthly granularity

Cost: ~2 calls per 100 apps per estimate scope.
Output: data/niche/enriched.json
Run: python scripts/niche_enrich.py [--budget N]
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from api.sensortower_client import SensorTowerClient  # noqa: E402

NICHE_DIR = PROJECT_ROOT / "data" / "niche"
BATCH = 100

# Fields worth keeping. Descriptions are truncated — we want them for feature
# analysis, not to carry 12MB of marketing copy around.
KEEP = [
    "app_id", "name", "subtitle", "publisher_name", "publisher_id", "rating",
    "rating_count", "global_rating_count", "rating_for_current_version",
    "rating_count_for_current_version", "price", "in_app_purchases", "version",
    "release_date", "updated_date", "categories", "supported_languages",
    "content_rating", "humanized_worldwide_last_month_downloads",
    "humanized_worldwide_last_month_revenue", "publisher_country",
    "apple_watch_enabled", "website_url",
]


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def fetch_details(client, app_ids):
    out = {}
    batches = list(chunks(app_ids, BATCH))
    for i, batch in enumerate(batches, 1):
        try:
            apps = client.get_app_details(batch, device="ios", use_cache=True)
        except Exception as e:
            print(f"  ! details batch {i}/{len(batches)}: {type(e).__name__}: {e}")
            continue
        for a in apps:
            rec = {k: a.get(k) for k in KEEP}
            desc = a.get("description") or ""
            rec["description_head"] = desc[:600]
            rec["description_len"] = len(desc)
            rec["n_screenshots"] = len(a.get("screenshot_urls") or [])
            out[str(a.get("app_id"))] = rec
        print(f"  details {i}/{len(batches)} -> {len(out)} apps")
    return out


def fetch_estimates(client, app_ids, months=12):
    """
    Downloads/revenue over the window, split US / TR / worldwide.

    The API's `country` parameter is silently ignored on this endpoint — it
    returns one record per (app, country, month) regardless — so one call gives
    us every scope and the split has to happen here on the `cc` field. That
    also means adding a new market costs zero API calls: the country is already
    in the cached response.
    `iu`/`ir` are iPhone units/revenue, `au`/`ar` the iPad half; both count.
    """
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=30 * months)).strftime("%Y-%m-%d")

    def blank():
        return {"us_downloads": 0, "us_revenue": 0.0,
                "tr_downloads": 0, "tr_revenue": 0.0,
                "ww_downloads": 0, "ww_revenue": 0.0}

    totals = defaultdict(blank)

    batches = list(chunks(app_ids, BATCH))
    for i, batch in enumerate(batches, 1):
        try:
            data = client.get_sales_estimates(
                app_ids=batch, device="ios", date_granularity="monthly",
                start_date=start, end_date=end, use_cache=True,
            )
        except Exception as e:
            print(f"  ! estimates batch {i}/{len(batches)}: {type(e).__name__}: {e}")
            continue

        records = data if isinstance(data, list) else data.get("data", [])
        for r in records:
            aid = str(r.get("aid"))
            if aid == "None":
                continue
            units = (r.get("iu") or 0) + (r.get("au") or 0)
            revenue = ((r.get("ir") or 0) + (r.get("ar") or 0)) / 100.0
            t = totals[aid]
            t["ww_downloads"] += units
            t["ww_revenue"] += revenue
            cc = r.get("cc")
            if cc == "US":
                t["us_downloads"] += units
                t["us_revenue"] += revenue
            elif cc == "TR":
                t["tr_downloads"] += units
                t["tr_revenue"] += revenue
        print(f"  estimates {i}/{len(batches)} -> {len(totals)} apps")

    return {k: dict(v) for k, v in totals.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=250)
    args = ap.parse_args()

    client = SensorTowerClient(cache_ttl_hours=72)
    start_usage = client.get_monthly_usage()
    print(f"Monthly usage before enrich: {start_usage}/2500")

    shortlist = json.loads((NICHE_DIR / "shortlist.json").read_text())
    app_ids = sorted(shortlist.keys(), key=int)
    print(f"Enriching {len(app_ids)} apps "
          f"(~{len(app_ids) // BATCH * 3 + 3} calls estimated)\n")

    print("Fetching app details...")
    details = fetch_details(client, app_ids)

    print("\nFetching sales estimates (12m; US, TR and worldwide in one pass)...")
    est = fetch_estimates(client, app_ids)

    merged = {}
    for aid, base in shortlist.items():
        d = details.get(aid, {})
        merged[aid] = {
            **base,
            "rating": d.get("rating"),
            "rating_count": d.get("rating_count"),
            "rating_current_version": d.get("rating_for_current_version"),
            "price": d.get("price"),
            "has_iap": d.get("in_app_purchases"),
            "version": d.get("version"),
            "supported_languages": d.get("supported_languages"),
            "n_languages": len(d.get("supported_languages") or []),
            "publisher_country": d.get("publisher_country"),
            "subtitle": d.get("subtitle"),
            "description_head": d.get("description_head"),
            "description_len": d.get("description_len"),
            "n_screenshots": d.get("n_screenshots"),
            "updated_date": d.get("updated_date", base.get("updated_date")) or base.get("updated_date"),
            "us_downloads_12m": est.get(aid, {}).get("us_downloads", 0),
            "us_revenue_12m": round(est.get(aid, {}).get("us_revenue", 0), 2),
            "tr_downloads_12m": est.get(aid, {}).get("tr_downloads", 0),
            "tr_revenue_12m": round(est.get(aid, {}).get("tr_revenue", 0), 2),
            "ww_downloads_12m": est.get(aid, {}).get("ww_downloads", 0),
            "ww_revenue_12m": round(est.get(aid, {}).get("ww_revenue", 0), 2),
        }

    (NICHE_DIR / "enriched.json").write_text(
        json.dumps(merged, indent=2, ensure_ascii=False))

    used = client.get_monthly_usage() - start_usage
    print(f"\nEnriched {len(merged)} apps -> data/niche/enriched.json")
    print(f"Calls used: {used}. Monthly: {client.get_monthly_usage()}/2500")


if __name__ == "__main__":
    main()
