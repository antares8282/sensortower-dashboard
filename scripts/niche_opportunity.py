"""
Phase 3: score sub-niches for "can we take this with a better app?". No API calls.

A category-level view hides the answer — "Religious" as a whole is huge and
crowded, but the functional sub-niches inside it behave completely differently.
So apps are bucketed by what they actually *do* (qibla finder, tasbih counter,
tide tables, anchor alarm...) and each bucket is scored on:

  demand      TR downloads over the last 12 months
  money       revenue per download — the single best signal of whether the
              niche monetizes at all
  crowding    how many live apps chase it, and how concentrated the leaders are
  weakness    leaders' ratings, and how many have gone stale (no update in 9m+)
  TR fit      whether the leaders actually ship Turkish

Output: data/niche/opportunities.json + reports/opportunity_scan_<date>.md
Run: python scripts/niche_opportunity.py
"""
import re
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.buildability import (  # noqa: E402
    buildability, barrier_note, top_barriers,
)

NICHE_DIR = PROJECT_ROOT / "data" / "niche"
REPORT_DIR = PROJECT_ROOT / "reports"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard_data" / "current"

STALE_DAYS = 275  # ~9 months without a release

# Revenue-per-download is a ratio, and ratios explode on small denominators:
# a niche with 1 US download and a subscription base still renewing reads as
# $141,141/download. Shrink toward zero with a pseudo-count so thin niches have
# to earn their way up, and separately flag anything under the volume floor as
# not yet measurable rather than pretending the number means something.
RPD_PRIOR = 2000
MIN_VOLUME = 10_000

# Primary market. Revenue estimates are IAP + paid only; ad revenue is invisible
# to this API, so a free app with no IAP reads as $0 no matter how well it earns.
MARKET = "us"

# Functional buckets. First match wins, so the more specific patterns lead.
SUBNICHES = [
    # --- religious ---
    ("religious", "Quran memorization / tajweed", r"tecvid|tajweed|hifz|memoriz|ezberle|hatim|elifba|kuran öğren|learn quran"),
    ("religious", "Quran reading / mushaf",       r"kur'?an|kur’an|quran|koran|mushaf|meal|ayet|sure|tefsir"),
    ("religious", "Prayer times / athan",         r"namaz|ezan|adhan|athan|prayer time|vakti|vakitleri|imsakiye"),
    ("religious", "Qibla finder",                 r"kıble|kible|qibla"),
    ("religious", "Tasbih / dhikr counter",       r"tesbih|tasbih|zikir|dhikr|zikirmatik|salavat"),
    ("religious", "Dua / supplication",           r"\bdua\b|dualar|supplication|esma"),
    ("religious", "Hadith / fiqh reference",      r"hadis|hadith|ilmihal|fıkıh|fiqh|siyer|risale"),
    ("religious", "Hajj / Umrah",                 r"\bhac\b|hajj|umre|umrah|mekke|medine|kabe|kaaba"),
    ("religious", "Ramadan / fasting",            r"ramazan|ramadan|oruç|iftar|sahur"),
    ("religious", "Mosque / community",           r"cami|camii|mosque|diyanet|hutbe|zekat|zakat|kurban|sadaka"),
    ("religious", "Islamic lifestyle (other)",    r"islam|müslüman|muslim|allah|peygamber|halal|helal|hicri|hijri|abdest"),
    ("religious", "Christian / other faith",      r"bible|incil|kilise|rosary"),

    # --- marine ---
    ("marine", "Charts / chartplotter",        r"chart|navionics|isailor|iboat|inavx|navigat|seyir|rota"),
    ("marine", "Weather / wind / routing",     r"wind|weather|forecast|routing|swell|windy|meteo|hava"),
    ("marine", "Tides & currents",             r"tide|gelgit|current"),
    ("marine", "AIS / vessel tracking",        r"\bais\b|vessel|traffic|ship track|marinetraffic"),
    ("marine", "Anchor watch / safety",        r"anchor|mooring|colreg|man overboard|safety|emergency"),
    ("marine", "Boat & yacht charter",         r"kirala|charter|rental|yat kiralama|tekne kiralama"),
    ("marine", "Logbook / maintenance",        r"logbook|log book|maintenance|seyir defteri|bakım"),
    ("marine", "Sailing training / theory",    r"skipper|amatör denizci|denizcilik|seamanship|terimleri|eğitim|akademi|course|exam|sınav|knot"),
    ("marine", "Racing / regatta",             r"regatta|race|racing|yarış|start line"),
    ("marine", "Fishing spots & forecast",     r"fish|balık|angler|trolling|solunar"),
    ("marine", "Diving / freediving",          r"dive|diving|dalış|scuba|spearfish|freediv"),
    ("marine", "Surf",                         r"surf"),
    ("marine", "Marina / harbour services",    r"marina|harbour|harbor|liman|port"),

    # --- vertical utility ---
    ("vertical_utility", "Agriculture / tractor", r"tractor|traktör|field|tarla|harvest|hasat|irrigation|sulama|sera|greenhouse|livestock|hayvancılık"),
    ("vertical_utility", "Beekeeping",            r"beekeep|arıcı|arici|apiary|hive|kovan"),
    ("vertical_utility", "Trades (elec/plumb/HVAC)", r"electric|elektrik|plumb|tesisat|hvac|weld|kaynak"),
    ("vertical_utility", "CNC / machining",       r"\bcnc\b|machinist|lathe|g-code|gcode|torna"),
    ("vertical_utility", "Trucking / logistics",  r"truck|kamyon|tır|forklift|warehouse|depo|logistic"),
    ("vertical_utility", "Radio / comms",         r"radio|telsiz|ham radio"),
    ("vertical_utility", "Outdoor (hunt/climb/cave)", r"hunt|avcılık|climb|tırmanış|caving|mağara"),
    ("vertical_utility", "Aviation / drone",      r"aviation|drone|flight log"),
]


def bucket(app):
    text = f"{app.get('name') or ''} {app.get('subtitle') or ''}".lower()
    for niche, label, pattern in SUBNICHES:
        if app["niche"] == niche and re.search(pattern, text, re.IGNORECASE):
            return label
    return f"{app['niche']} — unclassified"


def days_since(datestr):
    if not datestr:
        return None
    try:
        return (datetime.now() - datetime.fromisoformat(str(datestr)[:10])).days
    except ValueError:
        return None


def hhi(values):
    """Herfindahl index 0-1. >0.25 = one player owns the niche."""
    total = sum(values)
    if total <= 0:
        return None
    return round(sum((v / total) ** 2 for v in values), 3)


def analyse(apps, label, niche):
    live = [a for a in apps if a["us_downloads_12m"] > 0 or a["ww_downloads_12m"] > 0]
    us_dl = sum(a["us_downloads_12m"] for a in apps)
    us_rev = sum(a["us_revenue_12m"] for a in apps)
    tr_dl = sum(a["tr_downloads_12m"] for a in apps)
    tr_rev = sum(a["tr_revenue_12m"] for a in apps)
    ww_dl = sum(a["ww_downloads_12m"] for a in apps)
    ww_rev = sum(a["ww_revenue_12m"] for a in apps)

    # Free, no IAP, real downloads => almost certainly ad-supported, and its
    # revenue is entirely absent from these estimates. A niche where this is
    # common is under-measured, not necessarily unmonetized.
    ad_funded = [
        a for a in apps
        if a["us_downloads_12m"] > 1000
        and not a.get("has_iap") and (a.get("price") or 0) == 0
    ]
    ad_dl = sum(a["us_downloads_12m"] for a in ad_funded)

    leaders = sorted(apps, key=lambda a: -a["us_downloads_12m"])[:5]
    leaders_rated = [a for a in leaders if (a.get("rating") or 0) > 0]
    lead_rating = (round(sum(a["rating"] for a in leaders_rated) / len(leaders_rated), 2)
                   if leaders_rated else None)

    stale = [a for a in leaders if (days_since(a.get("updated_date")) or 0) > STALE_DAYS]
    tr_ready = [a for a in leaders if a.get("supports_turkish")]

    return {
        "sub_niche": label,
        "niche": niche,
        "apps_total": len(apps),
        "apps_with_downloads": len(live),
        "us_downloads_12m": us_dl,
        "us_revenue_12m": round(us_rev, 0),
        "us_rev_per_download": round(us_rev / us_dl, 3) if us_dl else 0,
        # Shrunk toward zero — this is what scoring uses.
        "us_rpd_smoothed": round(us_rev / (us_dl + RPD_PRIOR), 3),
        "low_volume": us_dl < MIN_VOLUME,
        "us_share_of_ww_rev": round(us_rev / ww_rev, 3) if ww_rev else 0,
        "tr_downloads_12m": tr_dl,
        "tr_revenue_12m": round(tr_rev, 0),
        "tr_rev_per_download": round(tr_rev / tr_dl, 3) if tr_dl else 0,
        "ww_downloads_12m": ww_dl,
        "ww_revenue_12m": round(ww_rev, 0),
        "ww_rev_per_download": round(ww_rev / ww_dl, 3) if ww_dl else 0,
        "ad_funded_apps": len(ad_funded),
        "ad_funded_download_share": round(ad_dl / us_dl, 3) if us_dl else 0,
        "hhi_us": hhi([a["us_downloads_12m"] for a in apps]),
        "leader_avg_rating": lead_rating,
        "leaders_stale_9m": len(stale),
        "leaders_supporting_turkish": len(tr_ready),
        "paid_apps": sum(1 for a in apps if (a.get("price") or 0) > 0),
        "iap_apps": sum(1 for a in apps if a.get("has_iap")),
        "buildability": buildability(label),
        "barrier_note": barrier_note(label),
        "top_barriers": top_barriers(label),
        "leaders": [
            {
                "app_id": a["app_id"],
                "name": a["name"],
                "publisher": a["publisher_name"],
                "us_downloads_12m": a["us_downloads_12m"],
                "us_revenue_12m": round(a["us_revenue_12m"], 0),
                "ww_downloads_12m": a["ww_downloads_12m"],
                "ww_revenue_12m": round(a["ww_revenue_12m"], 0),
                "rating": a.get("rating"),
                "global_rating_count": a.get("global_rating_count"),
                "updated_date": str(a.get("updated_date"))[:10],
                "days_since_update": days_since(a.get("updated_date")),
                "price": a.get("price"),
                "has_iap": a.get("has_iap"),
            }
            for a in leaders
        ],
    }


def market_score(row):
    """
    0-100 on market conditions alone: is there money here, and is it takeable?
    Monetization is weighted hardest — the scan's clearest lesson is that
    revenue per download separates real markets from volume traps by ~50x.
    """
    import math

    money = min(row["us_rpd_smoothed"] / 3.0, 1.0) * 40
    demand = min(math.log10(max(row["us_downloads_12m"], 1)) / 6.5, 1.0) * 20

    crowding = (1 - min(row["apps_with_downloads"] / 120, 1.0)) * 15

    rating = row["leader_avg_rating"]
    weakness = 0 if rating is None else max(0, (4.8 - rating) / 1.5) * 15
    weakness += min(row["leaders_stale_9m"] / 5, 1.0) * 10

    return round(money + demand + crowding + weakness, 1)


def go_score(market, build):
    """
    Geometric mean of market and buildability, so a niche has to clear both.
    An arithmetic mean would let a $45/download niche gated behind dive-computer
    firmware and decompression liability outrank something we could actually ship.
    """
    import math

    if build is None:
        return None
    return round(math.sqrt(max(market, 0) * max(build, 0)), 1)


def main():
    data = json.loads((NICHE_DIR / "enriched.json").read_text())
    apps = list(data.values())

    groups = defaultdict(list)
    for a in apps:
        groups[(a["niche"], bucket(a))].append(a)

    rows = []
    for (niche, label), members in groups.items():
        if len(members) < 3 or label.endswith("— unclassified"):
            # Unclassified is a keyword-matching residue, not a market.
            continue
        row = analyse(members, label, niche)
        row["market_score"] = market_score(row)
        row["go_score"] = go_score(row["market_score"], row["buildability"])
        # Ad revenue is invisible to the API, so flag niches where the revenue
        # figure is likely to understate reality rather than silently trusting it.
        row["ads_caveat"] = row["ad_funded_download_share"] > 0.35
        rows.append(row)

    # Measurable niches first; thin ones still listed, but never at the top.
    rows.sort(key=lambda r: (r["low_volume"], -(r["go_score"] or 0)))
    (NICHE_DIR / "opportunities.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False))

    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    (DASHBOARD_DIR / "niches.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False))

    # ---- console summary ----
    print(f"{'sub-niche':34s} {'apps':>5s} {'USdl':>10s} {'$/dl~':>7s} "
          f"{'rat':>5s} {'stale':>5s} {'ads':>4s} {'mkt':>5s} {'bld':>4s} {'GO':>5s}")
    for r in rows:
        if r["low_volume"]:
            continue
        print(f"{r['sub_niche'][:33]:34s} {r['apps_with_downloads']:5d} "
              f"{r['us_downloads_12m']:10,} {r['us_rpd_smoothed']:7.2f} "
              f"{(r['leader_avg_rating'] or 0):5.2f} {r['leaders_stale_9m']:5d} "
              f"{('yes' if r['ads_caveat'] else '-'):>4s} "
              f"{r['market_score']:5.1f} {(r['buildability'] or 0):4d} "
              f"{(r['go_score'] or 0):5.1f}")
    thin = [r["sub_niche"] for r in rows if r["low_volume"]]
    if thin:
        print(f"\nBelow {MIN_VOLUME:,} US downloads (not yet measurable): "
              f"{', '.join(thin)}")

    REPORT_DIR.mkdir(exist_ok=True)
    out = REPORT_DIR / f"opportunity_scan_{datetime.now():%Y%m%d}.md"
    write_report(out, rows)
    print(f"\nReport: {out}")
    print(f"Dashboard data: {DASHBOARD_DIR / 'niches.json'}")


def write_report(path, rows):
    L = []
    L.append(f"# iOS niche opportunity scan — {datetime.now():%Y-%m-%d}\n")
    L.append("Market: **US**, iOS only. Downloads/revenue are trailing 12 months, "
             "App Store estimates, iPhone + iPad combined.\n")
    L.append("`US $/dl` is revenue per download — the clearest read on whether a "
             "niche monetizes. **Ad revenue is not included** (the API reports IAP "
             "and paid only), so rows flagged `ads?` are under-measured.\n")
    L.append("`GO` is the geometric mean of market score and buildability, so a "
             "niche has to clear both to rank.\n")

    L.append("\n## Ranked sub-niches\n")
    L.append("| # | Sub-niche | Live apps | US dl 12m | US $/dl | Leader rating | Stale | Ads? | Market | Build | GO |")
    L.append("|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|")
    for i, r in enumerate(rows, 1):
        L.append(
            f"| {i} | {r['sub_niche']} | {r['apps_with_downloads']} | "
            f"{r['us_downloads_12m']:,} | ${r['us_rev_per_download']:.2f} | "
            f"{r['leader_avg_rating'] or '—'} | {r['leaders_stale_9m']}/5 | "
            f"{'yes' if r['ads_caveat'] else '—'} | {r['market_score']} | "
            f"{r['buildability'] if r['buildability'] is not None else '—'} | "
            f"**{r['go_score'] if r['go_score'] is not None else '—'}** |")

    L.append("\n## Detail per sub-niche\n")
    for r in rows:
        L.append(f"\n### {r['sub_niche']}  ·  GO {r['go_score']}\n")
        L.append(f"{r['apps_total']} apps matched ({r['apps_with_downloads']} with measurable "
                 f"downloads). US concentration HHI {r['hhi_us']}. "
                 f"{r['paid_apps']} paid, {r['iap_apps']} with IAP, "
                 f"{r['ad_funded_apps']} likely ad-funded "
                 f"({r['ad_funded_download_share']*100:.0f}% of US downloads). "
                 f"US is {r['us_share_of_ww_rev']*100:.0f}% of worldwide revenue.\n")
        if r["barrier_note"]:
            barriers = ", ".join(r["top_barriers"]) or "none dominant"
            L.append(f"**Build barriers** ({barriers}): {r['barrier_note']}\n")
        L.append("| App | Publisher | US dl | US rev | WW rev | Rating | Ratings | Last update |")
        L.append("|---|---|---:|---:|---:|---:|---:|---|")
        for a in r["leaders"]:
            L.append(
                f"| {a['name']} | {a['publisher']} | {a['us_downloads_12m']:,} | "
                f"${a['us_revenue_12m']:,.0f} | ${a['ww_revenue_12m']:,.0f} | "
                f"{a['rating'] or '—'} | {a['global_rating_count'] or 0:,} | "
                f"{a['updated_date']} ({a['days_since_update']}d) |")

    path.write_text("\n".join(L))


if __name__ == "__main__":
    main()
