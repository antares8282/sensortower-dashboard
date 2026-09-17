"""
Store-listing research for one app: who shows up for our terms, what they call
themselves, and how many downloads they get. Run by hand (or by the
store-listing-writer agent), never on a schedule.

This API plan has no keyword endpoints (traffic / difficulty all 404, see
data/probe2/_report.json), so keyword scores come from Sensor Tower web CSV
exports instead: pass --csv-dir and they are parsed alongside.

  1. ios/search_entities        one call per term      -> catalog matches
  2. ios/apps                   one call per 100 apps  -> name, subtitle, description
  3. ios/sales_report_estimates one call               -> worldwide downloads, 3 months

Everything is cached for a week by the client, so a re-run is nearly free.

Run:
  python scripts/aso_competitors.py --terms "yacht charter,gulet" \
      --apps 1479182650,933102632 --csv-dir /path/store-listing/sensortower \
      --out /path/store-listing/sensortower/research.json --budget 40
"""
import sys
import csv
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from api.sensortower_client import SensorTowerClient  # noqa: E402

PER_TERM = 15          # catalog matches kept per term
KEEP = ["app_id", "name", "subtitle", "publisher_name", "rating",
        "global_rating_count", "price", "categories", "updated_date"]


def read_aso_csv(path: Path):
    """Sensor Tower exports are UTF-16 tab-separated; return clean rows."""
    raw = path.read_bytes()
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig")
    rows = list(csv.DictReader(text.splitlines(), delimiter="\t"))
    num = lambda v: float(v) if v not in (None, "") else None
    out = []
    for r in rows:
        out.append({
            "keyword": r.get("Keyword"),
            "rank": num(r.get("Rank (for App)")),
            "traffic": num(r.get("Traffic Score")),
            "difficulty": num(r.get("Difficulty Score")),
            "opportunity": num(r.get("Opportunity Score")),
            "kw_downloads": num(r.get("KW Downloads (Absolute)")),
            "app_count": num(r.get("App Count")),
            "type": r.get("Keyword Type"),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", default="", help="comma-separated search terms")
    ap.add_argument("--apps", default="", help="comma-separated iOS app ids to always include")
    ap.add_argument("--csv-dir", help="folder of Sensor Tower ASO keyword CSV exports")
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget", type=int, default=40, help="max uncached API calls")
    a = ap.parse_args()

    client = SensorTowerClient()
    month = datetime.now().strftime("%Y-%m")
    start_usage = client.get_monthly_usage(month)
    spent = lambda: client.get_monthly_usage(month) - start_usage
    print(f"API calls this month before run: {start_usage}")

    terms = [t.strip() for t in a.terms.split(",") if t.strip()]
    pinned = [x.strip() for x in a.apps.split(",") if x.strip()]
    result = {"generated_at": datetime.now().isoformat(timespec="seconds"),
              "terms": {}, "apps": {}, "keyword_exports": {}}

    ids, seen_by = list(pinned), defaultdict(list)
    for t in terms:
        if spent() >= a.budget:
            print(f"  budget reached, skipping term '{t}'")
            continue
        try:
            hits = client.search_apps(t, limit=PER_TERM)
        except Exception as e:
            print(f"  ! search '{t}': {e}")
            continue
        result["terms"][t] = [{"app_id": h.get("app_id"), "name": h.get("name"),
                               "ratings": h.get("global_rating_count")} for h in hits]
        for h in hits:
            aid = str(h.get("app_id"))
            seen_by[aid].append(t)
            if aid not in ids:
                ids.append(aid)

    for i in range(0, len(ids), 100):
        if spent() >= a.budget:
            print("  budget reached, skipping details")
            break
        for app in client.get_app_details(ids[i:i + 100]):
            aid = str(app.get("app_id"))
            rec = {k: app.get(k) for k in KEEP}
            rec["description_head"] = (app.get("description") or "")[:800]
            rec["matched_terms"] = seen_by.get(aid, [])
            rec["pinned"] = aid in pinned
            result["apps"][aid] = rec

    if result["apps"] and spent() < a.budget:
        end = datetime.now()
        est = client.get_sales_estimates(
            app_ids=list(result["apps"])[:100], date_granularity="monthly",
            start_date=(end - timedelta(days=92)).strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"))
        dl = defaultdict(int)
        for r in est if isinstance(est, list) else []:
            dl[str(r.get("aid"))] += r.get("iu", 0) or 0
        for aid, rec in result["apps"].items():
            rec["downloads_3mo_ww"] = dl.get(aid, 0)

    if a.csv_dir:
        for f in sorted(Path(a.csv_dir).glob("*.csv")):
            result["keyword_exports"][f.name] = read_aso_csv(f)

    Path(a.out).write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print(f"API calls spent: {spent()} (budget {a.budget}) -> {a.out}")


if __name__ == "__main__":
    main()
