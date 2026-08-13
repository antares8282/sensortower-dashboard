"""
Re-apply classification rules to already-enriched apps. No API calls.

Classification rules get tuned often; download and revenue estimates do not.
Re-running niche_enrich after a rule change would re-batch different app_id
groups, miss every cache entry and spend ~400 calls to fetch data we already
hold. This reclassifies in place instead: apps that no longer qualify are
dropped, survivors get their family/sub_niche refreshed.

Run: python scripts/niche_reclassify.py
"""
import sys
import json
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from niche_filter import classify  # noqa: E402

NICHE_DIR = PROJECT_ROOT / "data" / "niche"


def main():
    catalog = json.loads((NICHE_DIR / "catalog.json").read_text())
    enriched = json.loads((NICHE_DIR / "enriched.json").read_text())

    kept, dropped, moved = {}, 0, 0
    for aid, app in enriched.items():
        source = catalog.get(aid)
        if not source:
            dropped += 1
            continue
        hit = classify(source)
        if not hit:
            dropped += 1
            continue
        family, sub = hit
        if app.get("family") != family or app.get("sub_niche") != sub:
            moved += 1
        app["family"], app["sub_niche"] = family, sub
        kept[aid] = app

    (NICHE_DIR / "enriched.json").write_text(
        json.dumps(kept, indent=2, ensure_ascii=False))

    print(f"kept {len(kept):,}  dropped {dropped:,}  reassigned {moved:,}")
    fams = Counter(a["family"] for a in kept.values())
    for f, n in fams.most_common():
        print(f"  {f:32s} {n:5d}")


if __name__ == "__main__":
    main()
