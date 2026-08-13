"""
Probe for any "downloadability" signal: ASO strength, keyword volume, paid ad
pressure, App Store featuring — anything that says how hard it is to actually
get installs in a niche, as opposed to how much money the niche makes.

Run: python scripts/probe_downloadability.py
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

BASE = "https://api.sensortower.com"
TOKEN = os.getenv("SENSORTOWER_API_TOKEN")
END = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
START = (datetime.now() - timedelta(days=32)).strftime("%Y-%m-%d")
APP = "553834731"      # Candy Crush — large, certain to have ad + ASO data
MARINE_APP = "744920098"  # Navionics

PROBES = [
    # ---- keyword / ASO ----
    ("kw research v1", "/v1/ios/keywords/research_keyword", {"term": "sailing", "country": "US"}),
    ("kw research (no country)", "/v1/ios/keywords/research_keyword", {"term": "sailing"}),
    ("kw current", "/v1/ios/keywords/get_current_keywords", {"app_id": APP, "country": "US"}),
    ("kw spy", "/v1/ios/keywords/keyword_spy", {"app_id": APP, "country": "US"}),
    ("kw ranks", "/v1/ios/keywords/get_keyword_rankings", {"app_id": APP, "country": "US"}),
    ("kw translate", "/v1/ios/keywords/translate", {"term": "sailing", "country": "US"}),
    ("aso keywords", "/v1/ios/aso/keywords", {"app_id": APP, "country": "US"}),
    ("search rankings", "/v1/ios/search_rankings",
     {"app_id": APP, "country": "US", "start_date": START, "end_date": END}),
    ("app keyword rank hist", "/v1/ios/keyword_rankings",
     {"app_ids": APP, "country": "US", "start_date": START, "end_date": END}),

    # ---- ad intelligence ----
    ("ad networks", "/v1/ios/ad_intel/networks", {}),
    ("ad network_analysis", "/v1/ios/ad_intel/network_analysis",
     {"app_ids": APP, "countries": "US", "start_date": START, "end_date": END,
      "period": "day"}),
    ("ad top_advertisers", "/v1/ios/ad_intel/top_advertisers",
     {"category": "6002", "country": "US", "date": END, "period": "week"}),
    ("ad top_publishers", "/v1/ios/ad_intel/top_publishers",
     {"category": "6002", "country": "US", "date": END, "period": "week"}),
    ("ad share_of_voice", "/v1/ios/ad_intel/share_of_voice",
     {"app_ids": APP, "countries": "US", "start_date": START, "end_date": END}),
    ("ad creatives", "/v1/ios/ad_intel/creatives",
     {"app_id": APP, "countries": "US", "start_date": START, "end_date": END,
      "networks": "Facebook", "ad_types": "video"}),
    ("ad impressions", "/v1/ios/ad_intel/impressions",
     {"app_ids": APP, "countries": "US", "start_date": START, "end_date": END}),
    ("ad intel bare", "/v1/ad_intel/network_analysis",
     {"app_ids": APP, "countries": "US", "start_date": START, "end_date": END}),

    # ---- App Store featuring (organic discovery pressure) ----
    ("featured today", "/v1/ios/featured/today/stories",
     {"country": "US", "start_date": START, "end_date": END}),
    ("featured apps", "/v1/ios/featured/apps",
     {"category": "6002", "country": "US", "start_date": START, "end_date": END}),
    ("featured creatives", "/v1/ios/featured/creatives",
     {"app_id": APP, "countries": "US", "start_date": START, "end_date": END}),

    # ---- category-level market context ----
    ("store summary (cat totals)", "/v1/ios/store_summary",
     {"categories": "6002", "countries": "US", "date_granularity": "monthly",
      "start_date": START, "end_date": END}),
    ("category ranking summary", "/v1/ios/category_ranking_summary",
     {"app_id": APP, "country": "US"}),
    ("download estimates by src", "/v1/ios/downloads_by_sources",
     {"app_ids": APP, "countries": "US", "start_date": START, "end_date": END}),
    ("app analysis: retention", "/v1/ios/usage/retention",
     {"app_ids": APP, "country": "US", "date_granularity": "all_time",
      "start_date": START, "end_date": END}),
    ("usage active users", "/v1/ios/usage/active_users",
     {"app_ids": APP, "countries": "US", "start_date": START, "end_date": END,
      "time_period": "month"}),
]


def probe(client, label, path, params):
    url = BASE + path
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
    except Exception as e:
        return {"label": label, "path": path, "status": "EXC", "note": str(e)[:120]}

    client._log_request(path)
    entry = {"label": label, "path": path, "status": r.status_code}

    if r.status_code == 200:
        try:
            data = r.json()
        except ValueError:
            entry["note"] = "non-JSON"
            return entry
        if isinstance(data, list):
            entry["shape"] = f"list[{len(data)}]"
            if data and isinstance(data[0], dict):
                entry["keys"] = sorted(data[0].keys())[:16]
        elif isinstance(data, dict):
            entry["shape"] = f"dict{sorted(data.keys())[:12]}"
            for k, v in data.items():
                if isinstance(v, list) and v:
                    entry[f"len_{k}"] = len(v)
                    if isinstance(v[0], dict):
                        entry[f"keys_{k}"] = sorted(v[0].keys())[:16]
        out = PROJECT_ROOT / "data" / "probe2" / (path.strip("/").replace("/", "_") + ".json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False)[:300000])
    else:
        body = r.text[:160]
        entry["note"] = "HTML 404" if "<!DOCTYPE" in body else body
    return entry


def main():
    client = SensorTowerClient(cache_ttl_hours=168)
    before = client.get_monthly_usage()
    print(f"Usage before: {before}    probes: {len(PROBES)}\n")

    results = []
    for label, path, params in PROBES:
        res = probe(client, label, path, params)
        ok = res["status"] == 200
        print(f"{'OK ' if ok else 'XX '}[{res['status']}] {label:28s} {path}")
        if ok:
            for k in ("shape",):
                if k in res:
                    print(f"      {res[k]}")
        results.append(res)
        time.sleep(0.6)

    after = client.get_monthly_usage()
    out = PROJECT_ROOT / "data" / "probe2" / "_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"probed_at": datetime.now().isoformat(), "calls": after - before,
         "results": results}, indent=2, ensure_ascii=False))

    ok = [r["label"] for r in results if r["status"] == 200]
    print(f"\nUsage after: {after} (+{after - before})")
    print(f"AVAILABLE ({len(ok)}/{len(results)}): {', '.join(ok) if ok else 'NONE'}")


if __name__ == "__main__":
    main()
