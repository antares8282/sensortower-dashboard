"""
Phase 1 of the opportunity scan: enumerate the candidate universe.

Two passes, both cached so re-runs cost nothing:
  A. Keyword sweep  — search_entities over the niche seed terms (catalog reach,
                      finds apps that never chart).
  B. Ranking sweep  — TR and US top charts for the categories these niches live
                      in (tells us who actually wins, and how deep the tail is).

Output: data/niche/{catalog.json, rankings_tr.json, rankings_us.json}
Run: python scripts/niche_scan.py [--budget N]
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from api.sensortower_client import SensorTowerClient  # noqa: E402
from config.niches import (  # noqa: E402
    NICHES, TR_SWEEP_CATEGORIES, US_SWEEP_CATEGORIES, CHARTS, IOS_CATEGORIES,
)

OUT_DIR = PROJECT_ROOT / "data" / "niche"
BUDGET_CAP = 2500


class Budget:
    """Hard stop so a sweep can never run away with the monthly quota."""

    def __init__(self, client, max_calls):
        self.client = client
        self.start = client.get_monthly_usage()
        self.max_calls = max_calls

    @property
    def used(self):
        return self.client.get_monthly_usage() - self.start

    def check(self):
        if self.used >= self.max_calls:
            raise RuntimeError(
                f"Budget cap hit: {self.used}/{self.max_calls} calls used this run."
            )


def keyword_sweep(client, budget, pages_per_term=1):
    """Search each seed term; dedupe by app_id, remember which terms hit it."""
    catalog = {}

    for niche, terms in NICHES.items():
        print(f"\n=== {niche} ({len(terms)} terms) ===")
        for term in terms:
            budget.check()
            for page in range(pages_per_term):
                try:
                    apps = client.search_apps(term, limit=250, offset=page * 250)
                except Exception as e:
                    print(f"  ! '{term}' page {page}: {type(e).__name__}: {e}")
                    break

                for a in apps:
                    aid = str(a.get("app_id"))
                    if not aid or aid == "None":
                        continue
                    rec = catalog.setdefault(aid, {**a, "_niches": [], "_terms": []})
                    if niche not in rec["_niches"]:
                        rec["_niches"].append(niche)
                    if term not in rec["_terms"]:
                        rec["_terms"].append(term)

                if len(apps) < 250:
                    break

            print(f"  {term:22s} -> catalog now {len(catalog)}")

    return catalog


def ranking_sweep(client, budget, categories, country, date):
    """Top charts per category × chart type. Raw app-id lists, no detail resolve."""
    out = {}
    for cat_id in categories:
        cat_name = IOS_CATEGORIES.get(cat_id, cat_id)
        out[cat_id] = {"name": cat_name, "charts": {}}
        for chart in CHARTS:
            budget.check()
            try:
                res = client.get_top_apps(
                    category=cat_id,
                    chart_type=chart,
                    country=country,
                    date=date,
                    resolve_details=False,
                )
                ids = [str(x) for x in res.get("ranking", [])]
            except Exception as e:
                print(f"  ! {country}/{cat_name}/{chart}: {type(e).__name__}: {e}")
                ids = []
            out[cat_id]["charts"][chart] = ids
            print(f"  {country} {cat_name:18s} {chart:26s} {len(ids):4d} apps")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=400,
                    help="max API calls this run (default 400)")
    ap.add_argument("--skip-rankings", action="store_true")
    ap.add_argument("--skip-search", action="store_true")
    args = ap.parse_args()

    client = SensorTowerClient(cache_ttl_hours=72)
    monthly = client.get_monthly_usage()
    print(f"Monthly usage before scan: {monthly}/{BUDGET_CAP}")
    if monthly >= 2000:
        print("WARNING: monthly usage above 2000 — aborting.")
        sys.exit(1)

    budget = Budget(client, args.budget)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ranking_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    try:
        if not args.skip_search:
            catalog = keyword_sweep(client, budget)
            (OUT_DIR / "catalog.json").write_text(
                json.dumps(catalog, indent=2, ensure_ascii=False))
            print(f"\nCatalog: {len(catalog)} unique apps -> data/niche/catalog.json")

        if not args.skip_rankings:
            print(f"\n=== TR ranking sweep ({ranking_date}) ===")
            tr = ranking_sweep(client, budget, TR_SWEEP_CATEGORIES, "TR", ranking_date)
            (OUT_DIR / "rankings_tr.json").write_text(json.dumps(tr, indent=2))

            print(f"\n=== US ranking sweep ({ranking_date}) ===")
            us = ranking_sweep(client, budget, US_SWEEP_CATEGORIES, "US", ranking_date)
            (OUT_DIR / "rankings_us.json").write_text(json.dumps(us, indent=2))

    except RuntimeError as e:
        print(f"\nSTOPPED: {e}")

    (OUT_DIR / "_scan_meta.json").write_text(json.dumps({
        "scanned_at": datetime.now().isoformat(),
        "ranking_date": ranking_date,
        "calls_used": budget.used,
        "monthly_usage": client.get_monthly_usage(),
    }, indent=2))

    print(f"\nDone. Calls used this run: {budget.used}. "
          f"Monthly: {client.get_monthly_usage()}/{BUDGET_CAP}")


if __name__ == "__main__":
    main()
