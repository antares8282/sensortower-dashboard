"""
Phase 1: sweep the catalog for every seed term.

search_entities is the only endpoint that reaches apps outside the top charts,
which is the entire point — an underserved niche is one where nobody charted,
so ranking data cannot see it by construction.

Output: data/niche/catalog.json
Run: python scripts/niche_scan.py [--budget N] [--pages N]
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from api.sensortower_client import SensorTowerClient  # noqa: E402
from config.niches import NICHE_DEFS, TOTAL_SEEDS  # noqa: E402

OUT_DIR = PROJECT_ROOT / "data" / "niche"


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
            raise RuntimeError(f"Budget cap hit: {self.used}/{self.max_calls}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=1200)
    ap.add_argument("--pages", type=int, default=1,
                    help="pages of 250 per seed term")
    args = ap.parse_args()

    client = SensorTowerClient(cache_ttl_hours=336)  # 14d — niches move slowly
    budget = Budget(client, args.budget)
    print(f"Monthly usage: {client.get_monthly_usage()}")
    print(f"Sweeping {TOTAL_SEEDS} seeds across {len(NICHE_DEFS)} families "
          f"({args.pages} page(s) each)\n")

    catalog = {}
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        for d in NICHE_DEFS:
            fam = d["family"]
            print(f"=== {fam} ({len(d['seeds'])} seeds) ===")
            for term in d["seeds"]:
                budget.check()
                for page in range(args.pages):
                    try:
                        apps = client.search_apps(term, limit=250, offset=page * 250)
                    except Exception as e:
                        print(f"  ! '{term}': {type(e).__name__}: {e}")
                        break
                    for a in apps:
                        aid = str(a.get("app_id"))
                        if not aid or aid == "None":
                            continue
                        rec = catalog.setdefault(
                            aid, {**a, "_families": [], "_terms": []})
                        if fam not in rec["_families"]:
                            rec["_families"].append(fam)
                        if term not in rec["_terms"]:
                            rec["_terms"].append(term)
                    if len(apps) < 250:
                        break
            print(f"  catalog now {len(catalog):,} apps  "
                  f"(calls {budget.used})")
    except RuntimeError as e:
        print(f"\nSTOPPED: {e}")

    (OUT_DIR / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False))
    (OUT_DIR / "_scan_meta.json").write_text(json.dumps({
        "scanned_at": datetime.now().isoformat(),
        "seeds": TOTAL_SEEDS,
        "families": len(NICHE_DEFS),
        "unique_apps": len(catalog),
        "calls_used": budget.used,
        "monthly_usage": client.get_monthly_usage(),
    }, indent=2))

    print(f"\nCatalog: {len(catalog):,} unique apps")
    print(f"Calls used: {budget.used}. Monthly: {client.get_monthly_usage()}")


if __name__ == "__main__":
    main()
