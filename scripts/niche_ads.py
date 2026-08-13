"""
Phase 2c: measure paid-advertising pressure per sub-niche.

This replaces the hand-scored buildability guess with something measured. The
question it answers is "how hard is it to actually get installs here" — if the
incumbents are all buying users, an organic launch starves; if nobody is
advertising, ASO and word of mouth can still win.

ad_intel/network_analysis is the only discovery-side signal this plan exposes.
Every keyword/ASO endpoint (research_keyword, get_current_keywords, keyword_spy,
search_rankings, aso/keywords) returns 404, and downloads_by_sources — which
would have given a clean organic-vs-paid split — returns 200 with permanently
empty data. So share of voice across ad networks is what we have.

`sov` is a per-app, per-network, per-day share of that network's impressions.
We sum it per app over the window as a relative spend-intensity proxy; it is
ordinal, not a dollar figure.

Output: data/niche/ad_pressure.json
Run: python scripts/niche_ads.py [--top N] [--budget N]
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
load_dotenv(PROJECT_ROOT / ".env")

from api.sensortower_client import SensorTowerClient  # noqa: E402

NICHE_DIR = PROJECT_ROOT / "data" / "niche"
ENDPOINT = "/v1/ios/ad_intel/network_analysis"
BATCH = 5           # hard server limit: "Too many app IDs. The limit is 5."
WINDOW_DAYS = 90


def fetch(client, token, app_ids, start, end):
    """sov totals + network count per app_id."""
    url = "https://api.sensortower.com" + ENDPOINT
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    params = {
        "app_ids": ",".join(app_ids),
        "countries": "US",
        "start_date": start,
        "end_date": end,
        "period": "day",
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=60)
    except Exception as e:
        print(f"    ! {type(e).__name__}: {e}")
        return {}
    client._log_request(ENDPOINT)
    if r.status_code != 200:
        print(f"    ! HTTP {r.status_code}: {r.text[:110]}")
        return {}

    out = defaultdict(lambda: {"sov": 0.0, "networks": set(), "days": set()})
    for rec in r.json():
        aid = str(rec.get("app_id"))
        o = out[aid]
        o["sov"] += rec.get("sov") or 0
        if rec.get("network"):
            o["networks"].add(rec["network"])
        if rec.get("date"):
            o["days"].add(rec["date"])
    return {
        k: {"sov": round(v["sov"], 6),
            "networks": len(v["networks"]),
            "active_days": len(v["days"])}
        for k, v in out.items()
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5,
                    help="apps per sub-niche to sample, by US downloads")
    ap.add_argument("--budget", type=int, default=400)
    args = ap.parse_args()

    token = os.getenv("SENSORTOWER_API_TOKEN")
    client = SensorTowerClient()
    start_usage = client.get_monthly_usage()

    enriched = json.loads((NICHE_DIR / "enriched.json").read_text())

    # Sample the leaders of each sub-niche — advertising concentrates at the
    # top, and querying all ~20k apps would be absurd.
    by_sub = defaultdict(list)
    for a in enriched.values():
        by_sub[(a["family"], a["sub_niche"])].append(a)

    sampled = []
    for key, apps in by_sub.items():
        apps.sort(key=lambda a: -a.get("us_downloads_12m", 0))
        sampled.extend(a["app_id"] for a in apps[:args.top]
                       if a.get("us_downloads_12m", 0) > 0)
    sampled = sorted(set(sampled))

    end = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=WINDOW_DAYS)).strftime("%Y-%m-%d")
    print(f"Sampling {len(sampled)} apps across {len(by_sub)} sub-niches "
          f"({start} → {end})")
    print(f"~{(len(sampled) + BATCH - 1)//BATCH} calls\n")

    results = {}
    batches = [sampled[i:i + BATCH] for i in range(0, len(sampled), BATCH)]
    for i, batch in enumerate(batches, 1):
        if client.get_monthly_usage() - start_usage >= args.budget:
            print("Budget cap reached — stopping.")
            break
        results.update(fetch(client, token, batch, start, end))
        advertisers = sum(1 for v in results.values() if v["sov"] > 0)
        print(f"  batch {i}/{len(batches)} -> {len(results)} apps, "
              f"{advertisers} advertising")
        time.sleep(0.4)

    # The endpoint returns rows only for apps that actually ran ads, so an
    # app missing from `results` means "queried, not advertising" — not "no
    # data". Record the queried set explicitly so scoring can tell the two
    # apart instead of silently treating non-advertisers as unsampled.
    (NICHE_DIR / "ad_pressure.json").write_text(json.dumps({
        "measured_at": datetime.now().isoformat(),
        "window": {"start": start, "end": end},
        "sampled_apps": len(sampled),
        "queried": sampled,
        "apps": results,
    }, indent=2))

    used = client.get_monthly_usage() - start_usage
    print(f"\nAd data for {len(results)} apps. Calls: {used}. "
          f"Monthly: {client.get_monthly_usage()}")


if __name__ == "__main__":
    main()
