"""
Phase 2a: turn the raw keyword sweep into a defensible niche membership list.

search_entities is fuzzy — a search for "kuran" also returns "Kredit Pintar" and
"GoPay Merchant". So an app only counts as a niche member if its *name* carries a
strong niche token AND it sits in a plausible category. No API calls here.

Output: data/niche/shortlist.json
Run: python scripts/niche_filter.py
"""
import re
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.niches import IOS_CATEGORIES  # noqa: E402

NICHE_DIR = PROJECT_ROOT / "data" / "niche"

# Strong tokens: presence in an app name is near-conclusive for the niche.
STRONG = {
    "religious": [
        "kuran", "kur'an", "kur’an", "quran", "koran", "namaz", "ezan", "adhan",
        "athan", "kıble", "kible", "qibla", "dua", "zikir", "dhikr", "tesbih",
        "tasbih", "hadis", "hadith", "ilmihal", "esmaül", "esmaul", "tefsir",
        "meali", "umre", "umrah", "hac ", "hajj", "ramazan", "ramadan",
        "imsakiye", "mevlid", "yasin", "cevşen", "cevsen", "hatim", "elifba",
        "tecvid", "tajweed", "islam", "islâm", "müslüman", "muslim", "abdest",
        "peygamber", "siyer", "risale", "salavat", "ayet", "diyanet",
        "cami", "mosque", "hutbe", "zekat", "zakat", "kurban", "allah",
        "mekke", "medine", "kabe", "kaaba", "hijri", "hicri", "halal", "helal",
        "prayer time", "namaz vakti", "ezan vakti", "bible", "incil", "kilise",
        "rosary", "tesbihat", "sadaka", "oruç", "iftar", "sahur",
    ],
    "marine": [
        "sail", "yelken", "yacht", "boat", "tekne", "marine", "denizci",
        "nautical", "chartplotter", "navionics", "anchor", "tide", "gelgit",
        "regatta", "marina", "mooring", "skipper", "colreg", "buoy", "şamandıra",
        "catamaran", "dinghy", "surf", "dive", "diving", "dalış", "scuba",
        "spearfish", "fishing", "balık", "angler", "vhf", "ais", "seamanship",
        "harbour", "harbor",
        "offshore", "cruising", "navtex", "windy", "swell", "trolling",
    ],
    "vertical_utility": [
        "beekeep", "arıcı", "arici", "apiary", "hive", "kovan", "greenhouse",
        "sera ", "irrigation", "sulama", "livestock", "hayvancılık", "tractor",
        "traktör", "harvest", "hasat", "welding", "kaynak makine", "cnc",
        "machinist", "electrician", "elektrikçi", "plumber", "tesisat", "hvac",
        "solar panel", "güneş panel", "forklift", "warehouse", "depo yönetim",
        "amateur radio", "ham radio", "telsiz", "drone log", "logbook",
        "caving", "mağara", "climbing", "tırmanış", "hunting", "avcılık",
        "kamyon", "truck driver", "trucker",
    ],
}

# Tokens are matched on word boundaries, not raw substrings: "sure" inside
# "Tape Measure" and "dive" inside "Flip Diving" produced a shortlist full of
# blood-pressure trackers and arcade games on the first pass.
TOKEN_RE = {
    niche: re.compile(
        "|".join(r"\b" + re.escape(t.strip()) + r"\b" for t in toks),
        re.IGNORECASE,
    )
    for niche, toks in STRONG.items()
}

# Games are never the target here — these are all tool/utility theses, and
# fishing/hunting/sailing simulators otherwise dominate the download rankings.
GAMES_CATEGORY = 6014

# Categories where each niche plausibly lives. Anything outside is noise.
PLAUSIBLE_CATS = {
    "religious": {6012, 6006, 6018, 6017, 6016, 6013, 6002, 6011, 6009},
    "marine": {6002, 6010, 6003, 6004, 6001, 6013, 6006, 6017, 6016},
    "vertical_utility": {6002, 6000, 6007, 6010, 6006, 6017, 6004, 6001, 6003},
}

NICHE_OF = {
    "religious_tr": "religious",
    "religious_global": "religious",
    "marine": "marine",
    "vertical_utility": "vertical_utility",
}

# Two separate tests. The diacritic class must stay case-SENSITIVE: under
# IGNORECASE Python folds dotless "ı" onto "i", which flags every English name
# containing an i ("Fishing", "Navionics"). ö/ü are excluded — too German/Nordic
# to be evidence of Turkish on their own.
TR_DIACRITIC = re.compile(r"[çÇğĞışŞİ]")
TR_TOKENS = re.compile(
    r"\b(kuran|kur'an|namaz|ezan|kible|dua|dualar|zikir|tesbih|meali|vakti|"
    r"vakitleri|turk\w*|türk\w*|turkce|yelken|tekne|denizci\w*|balik\w*|dalis|"
    r"arici\w*|traktor|ayet|hatim|elifba|imsakiye|oruc|iftar|sahur|abdest|"
    r"hutbe|zekat|kurban|cami|camii|diyanet|sesli|dinle|ogren)\b",
    re.IGNORECASE,
)


def is_turkish(name):
    return bool(TR_DIACRITIC.search(name or "") or TR_TOKENS.search(name or ""))


def norm(s):
    return (s or "").lower().replace("’", "'")


def classify(app):
    """Return the niche this app genuinely belongs to, or None."""
    name = norm(app.get("name")) + " " + norm(app.get("humanized_name"))
    cats = set(app.get("categories") or [])

    if GAMES_CATEGORY in cats:
        return None

    # Only consider niches the search actually surfaced it under.
    candidates = {NICHE_OF[n] for n in app.get("_niches", []) if n in NICHE_OF}

    for niche in candidates:
        if not TOKEN_RE[niche].search(name):
            continue
        if cats and not (cats & PLAUSIBLE_CATS[niche]):
            continue
        return niche
    return None


def main():
    catalog = json.loads((NICHE_DIR / "catalog.json").read_text())
    tr = json.loads((NICHE_DIR / "rankings_tr.json").read_text())
    us = json.loads((NICHE_DIR / "rankings_us.json").read_text())

    def rank_index(rankings):
        """app_id -> best (category, chart, position)."""
        idx = {}
        for cat_id, cat in rankings.items():
            for chart, ids in cat["charts"].items():
                for pos, aid in enumerate(ids, 1):
                    prev = idx.get(aid)
                    if prev is None or pos < prev["rank"]:
                        idx[aid] = {"category": cat["name"], "chart": chart, "rank": pos}
        return idx

    tr_idx, us_idx = rank_index(tr), rank_index(us)

    shortlist = {}
    for aid, app in catalog.items():
        niche = classify(app)
        if not niche:
            continue
        if app.get("active") is False:
            continue

        name = app.get("name") or ""
        valid = set(app.get("valid_countries") or [])
        rec = {
            "app_id": aid,
            "name": name,
            "publisher_name": app.get("publisher_name"),
            "publisher_id": app.get("publisher_id"),
            "niche": niche,
            "categories": [IOS_CATEGORIES.get(str(c), str(c)) for c in (app.get("categories") or [])],
            "category_ids": app.get("categories") or [],
            "global_rating_count": app.get("global_rating_count") or 0,
            "release_date": (app.get("release_date") or "")[:10],
            "updated_date": (app.get("updated_date") or "")[:10],
            "available_tr": "TR" in valid,
            "turkish_signal": is_turkish(name),
            "tr_rank": tr_idx.get(aid),
            "us_rank": us_idx.get(aid),
            "matched_terms": app.get("_terms", [])[:8],
        }
        shortlist[aid] = rec

    (NICHE_DIR / "shortlist.json").write_text(
        json.dumps(shortlist, indent=2, ensure_ascii=False))

    from collections import Counter
    by_niche = Counter(r["niche"] for r in shortlist.values())
    print(f"Shortlist: {len(shortlist)} apps")
    for k, v in by_niche.most_common():
        sub = [r for r in shortlist.values() if r["niche"] == k]
        print(f"  {k:18s} {v:5d}   TR-available {sum(r['available_tr'] for r in sub):5d}"
              f"   TR-charting {sum(bool(r['tr_rank']) for r in sub):4d}"
              f"   turkish-named {sum(r['turkish_signal'] for r in sub):5d}")


if __name__ == "__main__":
    main()
