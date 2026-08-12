"""
Probe which SensorTower endpoints this subscription exposes.

Purpose: determine how much of the iOS catalog we can actually enumerate
(full search vs. ranking-only), before committing API budget to a big pull.

Every call is logged to data/api_usage_log.json so the budget stays accurate.
Run: python scripts/probe_capabilities.py
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
load_dotenv(PROJECT_ROOT / ".env")

from api.sensortower_client import SensorTowerClient  # noqa: E402

BASE_URL = "https://api.sensortower.com/v1"
TOKEN = os.getenv("SENSORTOWER_API_TOKEN")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
LAST_MONTH = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")

# Turkish religious app used as a live test subject (Diyanet / Kuran style app).
# Resolved dynamically from the TR ranking probe if possible.
FALLBACK_APP = "479516143"  # Quran Majeed

PROBES = [
    # (label, endpoint, params) — ordered cheapest/most-important first
    ("ranking TR Lifestyle", "ios/ranking",
     {"category": "6012", "chart_type": "topfreeapplications", "country": "TR", "date": YESTERDAY}),
    ("ranking TR Reference", "ios/ranking",
     {"category": "6006", "chart_type": "topfreeapplications", "country": "TR", "date": YESTERDAY}),
    ("ranking TR Utilities grossing", "ios/ranking",
     {"category": "6002", "chart_type": "topgrossingapplications", "country": "TR", "date": YESTERDAY}),

    # --- catalog enumeration: the key question ---
    ("search_entities (keyword catalog search)", "ios/search_entities",
     {"entity_type": "app", "term": "kuran", "limit": 25}),
    ("top_and_trending", "ios/top_and_trending",
     {"category": "6012", "country": "TR", "date": LAST_MONTH, "measure": "units",
      "date_granularity": "monthly", "limit": 25}),
    ("top_publishers", "ios/top_and_trending/publishers",
     {"category": "6012", "country": "TR", "date": LAST_MONTH, "measure": "units",
      "date_granularity": "monthly", "limit": 25}),

    # --- ASO / keyword intelligence (demand-side sizing) ---
    ("keyword research", "ios/keywords/research_keyword",
     {"term": "kuran", "country": "TR"}),
    ("app current keywords", "ios/keywords/get_current_keywords",
     {"app_id": FALLBACK_APP, "country": "TR"}),

    # --- monetization / quality signals ---
    ("top in-app purchases", "ios/apps/top_in_app_purchases",
     {"app_ids": FALLBACK_APP, "country": "TR"}),
    ("review history", "ios/review_history",
     {"app_id": FALLBACK_APP, "country": "TR", "start_date": LAST_MONTH, "end_date": YESTERDAY}),
    ("reviews", "ios/reviews",
     {"app_id": FALLBACK_APP, "country": "TR", "start_date": LAST_MONTH, "end_date": YESTERDAY, "limit": 10}),
    ("app update timeline", "ios/app_update_history",
     {"app_id": FALLBACK_APP, "country": "TR"}),

    # --- engagement (usually a separate SKU) ---
    ("active users (usage intel)", "ios/usage/active_users",
     {"app_ids": FALLBACK_APP, "countries": "TR", "start_date": LAST_MONTH,
      "end_date": YESTERDAY, "time_period": "month"}),
    ("retention", "ios/usage/retention",
     {"app_ids": FALLBACK_APP, "country": "TR", "date_granularity": "all_time"}),
    ("demographics", "ios/usage/demographics",
     {"app_ids": FALLBACK_APP, "country": "TR", "date_granularity": "all_time"}),

    # --- store/category metadata ---
    ("category history", "ios/category_history",
     {"app_ids": FALLBACK_APP, "categories": "6012", "chart_type_ids": "topfreeapplications",
      "countries": "TR", "start_date": LAST_MONTH, "end_date": YESTERDAY}),
    ("store summary", "ios/store_summary",
     {"categories": "6012", "countries": "TR", "date_granularity": "monthly",
      "start_date": LAST_MONTH, "end_date": YESTERDAY}),
]


def probe(client, label, endpoint, params):
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
    except Exception as e:
        return {"label": label, "endpoint": endpoint, "status": "EXC", "note": str(e)[:120]}

    # Every hit counts against quota, success or not.
    client._log_request(endpoint)

    entry = {"label": label, "endpoint": endpoint, "status": r.status_code}
    if r.status_code == 200:
        try:
            data = r.json()
        except ValueError:
            entry["note"] = "non-JSON body"
            return entry
        if isinstance(data, list):
            entry["shape"] = f"list[{len(data)}]"
            entry["sample_keys"] = sorted(data[0].keys())[:14] if data and isinstance(data[0], dict) else None
        elif isinstance(data, dict):
            entry["shape"] = f"dict{sorted(data.keys())[:10]}"
            for k, v in data.items():
                if isinstance(v, list):
                    entry[f"len_{k}"] = len(v)
                    if v and isinstance(v[0], dict):
                        entry[f"keys_{k}"] = sorted(v[0].keys())[:14]
        out = PROJECT_ROOT / "data" / "probe" / f"{endpoint.replace('/', '_')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False)[:400000])
    else:
        entry["note"] = r.text[:180]
    return entry


def main():
    client = SensorTowerClient(cache_ttl_hours=168)
    before = client.get_monthly_usage()
    print(f"API usage before probe: {before}/2500  ({len(PROBES)} probe calls planned)\n")

    results = []
    for label, endpoint, params in PROBES:
        res = probe(client, label, endpoint, params)
        flag = "OK " if res["status"] == 200 else "XX "
        print(f"{flag} [{res['status']}] {label:38s} {endpoint}")
        if res["status"] != 200:
            print(f"      -> {res.get('note', '')}")
        results.append(res)
        time.sleep(1.0)

    after = client.get_monthly_usage()
    print(f"\nAPI usage after probe: {after}/2500 (+{after - before})")

    out = PROJECT_ROOT / "data" / "probe" / "_capability_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"probed_at": datetime.now().isoformat(), "calls_used": after - before, "results": results},
        indent=2, ensure_ascii=False))
    print(f"Report: {out}")

    ok = [r["label"] for r in results if r["status"] == 200]
    print(f"\nAvailable ({len(ok)}/{len(results)}): {', '.join(ok)}")


if __name__ == "__main__":
    main()
