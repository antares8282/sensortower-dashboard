"""
Phase 2a: confirm niche membership and assign a sub-niche. No API calls.

search_entities is fuzzy — searching "sailing" also returns loan apps and
ride-hailing. An app only counts if, for a family the search actually surfaced
it under, its name/subtitle matches one of that family's sub-niche patterns AND
it sits in a plausible category for that family.

Games are excluded outright: every one of these theses is tool-shaped, and
fishing/hunting/farming simulators otherwise dominate the download rankings.

Output: data/niche/shortlist.json
Run: python scripts/niche_filter.py
"""
import re
import sys
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.niches import (  # noqa: E402
    NICHE_DEFS, IOS_CATEGORIES, GAMES_CATEGORY, FAMILY_GUARDS, family_index,
)

NICHE_DIR = PROJECT_ROOT / "data" / "niche"


def anchor(pattern):
    """
    Prefix every alternative with \\b so stems match at word starts only.
    Without this, `hos` (hours-of-service) matched inside "Harvest Hosts",
    putting an RV-camping app at the top of trucking compliance. Alternatives
    that already begin with an escape or boundary are left alone.
    """
    parts = []
    for alt in pattern.split("|"):
        parts.append(alt if alt.startswith(("\\b", "\\", "(")) else r"\b" + alt)
    return "|".join(parts)


COMPILED = {
    d["family"]: [(lbl, re.compile(anchor(pat), re.IGNORECASE))
                  for lbl, pat in d["subniches"]]
    for d in NICHE_DEFS
}
GUARDS = {fam: re.compile(anchor(pat), re.IGNORECASE)
          for fam, pat in FAMILY_GUARDS.items()}
FAMILIES = family_index()


def classify(app):
    """Return (family, sub_niche) or None."""
    cats = set(app.get("categories") or [])
    if GAMES_CATEGORY in cats:
        return None

    text = f"{app.get('name') or ''} {app.get('humanized_name') or ''}".lower()

    for fam in app.get("_families", []):
        d = FAMILIES.get(fam)
        if not d:
            continue
        if cats and not (cats & d["categories"]):
            continue
        # The name must actually belong to this domain, not merely trip a
        # generic sub-niche stem borrowed from another family.
        guard = GUARDS.get(fam)
        if guard and not guard.search(text):
            continue
        for label, rx in COMPILED[fam]:
            if rx.search(text):
                return fam, label
    return None


def main():
    catalog = json.loads((NICHE_DIR / "catalog.json").read_text())

    shortlist = {}
    for aid, app in catalog.items():
        if app.get("active") is False:
            continue
        hit = classify(app)
        if not hit:
            continue
        family, sub_niche = hit
        shortlist[aid] = {
            "app_id": aid,
            "name": app.get("name") or "",
            "publisher_name": app.get("publisher_name"),
            "publisher_id": app.get("publisher_id"),
            "family": family,
            "sub_niche": sub_niche,
            "categories": [IOS_CATEGORIES.get(str(c), str(c))
                           for c in (app.get("categories") or [])],
            "category_ids": app.get("categories") or [],
            "global_rating_count": app.get("global_rating_count") or 0,
            "release_date": (app.get("release_date") or "")[:10],
            "updated_date": (app.get("updated_date") or "")[:10],
            "matched_terms": app.get("_terms", [])[:8],
        }

    (NICHE_DIR / "shortlist.json").write_text(
        json.dumps(shortlist, indent=2, ensure_ascii=False))

    by_fam = Counter(r["family"] for r in shortlist.values())
    print(f"Catalog {len(catalog):,} -> shortlist {len(shortlist):,} apps\n")
    for fam, n in by_fam.most_common():
        subs = Counter(r["sub_niche"] for r in shortlist.values()
                       if r["family"] == fam)
        print(f"{fam:32s} {n:5d}   {len(subs)} sub-niches")


if __name__ == "__main__":
    main()
