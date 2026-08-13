"""
Phase 3: score sub-niches. No API calls.

Category-level views hide the answer — "Utilities" contains both flashlight
apps and $33/download marine chartplotters — so apps are bucketed by what they
actually do, and each bucket scored on:

  money       revenue per download, the single best signal of whether a niche
              monetizes at all (it separates markets by ~50x)
  demand      US downloads over the trailing 12 months
  crowding    how many live apps chase it
  weakness    leaders' ratings and how many have gone stale
  ad pressure how much paid user acquisition the leaders are running — the only
              discovery-side signal this API plan exposes

Output: data/niche/opportunities.json, dashboard_data/current/niches.json,
        reports/opportunity_scan_<date>.md
Run: python scripts/niche_opportunity.py
"""
import sys
import json
import math
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

NICHE_DIR = PROJECT_ROOT / "data" / "niche"
REPORT_DIR = PROJECT_ROOT / "reports"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard_data" / "current"

STALE_DAYS = 275   # ~9 months without a release

# Revenue per download is a ratio, and ratios explode on small denominators: a
# niche with 1 download and a still-renewing subscription base read as
# $141,141/download and ranked near the top. Shrink toward zero with a
# pseudo-count, and separately flag anything under the floor as not measurable.
RPD_PRIOR = 2000
MIN_VOLUME = 10_000


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


def load_ads():
    """
    Returns (per_app_stats, queried_ids).

    The ad-intel endpoint emits rows only for apps that actually advertised, so
    an app absent from `apps` but present in `queried` is a confirmed
    non-advertiser — the most useful signal here. Conflating that with
    "never sampled" would wrongly mark open niches as unmeasured.
    """
    path = NICHE_DIR / "ad_pressure.json"
    if not path.exists():
        return {}, set()
    d = json.loads(path.read_text())
    return d.get("apps", {}), {str(x) for x in d.get("queried", [])}


def analyse(apps, family, label, ads, queried):
    live = [a for a in apps if a["us_downloads_12m"] > 0 or a["ww_downloads_12m"] > 0]
    us_dl = sum(a["us_downloads_12m"] for a in apps)
    us_rev = sum(a["us_revenue_12m"] for a in apps)
    ww_dl = sum(a["ww_downloads_12m"] for a in apps)
    ww_rev = sum(a["ww_revenue_12m"] for a in apps)

    # Free, no IAP, real downloads => almost certainly ad-funded, and that
    # revenue is entirely absent from these estimates. Common here means the
    # niche is under-measured, not unmonetized.
    ad_funded = [
        a for a in apps
        if a["us_downloads_12m"] > 1000
        and not a.get("has_iap") and (a.get("price") or 0) == 0
    ]
    ad_dl = sum(a["us_downloads_12m"] for a in ad_funded)

    leaders = sorted(apps, key=lambda a: -a["us_downloads_12m"])[:10]

    # --- paid UA pressure among the leaders we sampled ---
    sampled = [a for a in leaders if str(a["app_id"]) in queried]
    advertisers = [a for a in sampled
                   if ads.get(str(a["app_id"]), {}).get("sov", 0) > 0]
    total_sov = sum(ads.get(str(a["app_id"]), {}).get("sov", 0) for a in sampled)
    ad_share = len(advertisers) / len(sampled) if sampled else None

    leaders_rated = [a for a in leaders[:5] if (a.get("rating") or 0) > 0]
    lead_rating = (round(sum(a["rating"] for a in leaders_rated) / len(leaders_rated), 2)
                   if leaders_rated else None)
    stale = [a for a in leaders[:5]
             if (days_since(a.get("updated_date")) or 0) > STALE_DAYS]

    return {
        "sub_niche": label,
        "family": family,
        "apps_total": len(apps),
        "apps_with_downloads": len(live),
        "us_downloads_12m": us_dl,
        "us_revenue_12m": round(us_rev, 0),
        "us_rev_per_download": round(us_rev / us_dl, 3) if us_dl else 0,
        "us_rpd_smoothed": round(us_rev / (us_dl + RPD_PRIOR), 3),
        "low_volume": us_dl < MIN_VOLUME,
        "ww_downloads_12m": ww_dl,
        "ww_revenue_12m": round(ww_rev, 0),
        "us_share_of_ww_rev": round(us_rev / ww_rev, 3) if ww_rev else 0,
        "ad_funded_apps": len(ad_funded),
        "ad_funded_download_share": round(ad_dl / us_dl, 3) if us_dl else 0,
        "ads_caveat": (ad_dl / us_dl if us_dl else 0) > 0.35,
        "ua_sampled": len(sampled),
        "ua_advertisers": len(advertisers),
        "ua_advertiser_share": round(ad_share, 3) if ad_share is not None else None,
        "ua_total_sov": round(total_sov, 4),
        "hhi_us": hhi([a["us_downloads_12m"] for a in apps]),
        "leader_avg_rating": lead_rating,
        "leaders_stale_9m": len(stale),
        "paid_apps": sum(1 for a in apps if (a.get("price") or 0) > 0),
        "iap_apps": sum(1 for a in apps if a.get("has_iap")),
        "leaders": [
            {
                "app_id": a["app_id"],
                "name": a["name"],
                "publisher": a["publisher_name"],
                "us_downloads_12m": a["us_downloads_12m"],
                "us_revenue_12m": round(a["us_revenue_12m"], 0),
                "ww_revenue_12m": round(a["ww_revenue_12m"], 0),
                "rating": a.get("rating"),
                "global_rating_count": a.get("global_rating_count"),
                "updated_date": str(a.get("updated_date"))[:10],
                "days_since_update": days_since(a.get("updated_date")),
                "price": a.get("price"),
                "has_iap": a.get("has_iap"),
                "ua_sov": ads.get(str(a["app_id"]), {}).get("sov"),
            }
            for a in leaders[:5]
        ],
    }


def score(row):
    """
    0-100. Money is weighted hardest; paid-UA pressure is a penalty, because a
    niche where every leader is buying installs is one an organic launch cannot
    enter regardless of how good the app is.
    """
    money = min(row["us_rpd_smoothed"] / 3.0, 1.0) * 32
    demand = min(math.log10(max(row["us_downloads_12m"], 1)) / 6.5, 1.0) * 20
    crowding = (1 - min(row["apps_with_downloads"] / 120, 1.0)) * 15

    rating = row["leader_avg_rating"]
    weakness = 0 if rating is None else max(0, (4.8 - rating) / 1.5) * 13
    weakness += min(row["leaders_stale_9m"] / 5, 1.0) * 8

    # Unmeasured UA (nothing sampled) scores neutral rather than free marks.
    share = row["ua_advertiser_share"]
    if share is None:
        openness = 6.0
    else:
        openness = (1 - share) * 12

    raw = money + demand + crowding + weakness + openness

    # A niche one strong incumbent already owns is not enterable, however well
    # it monetizes: genealogy scores beautifully until you notice Ancestry holds
    # 80% of downloads at 4.77 stars and ships every week. Penalise concentration
    # only when the leader is also well-rated — a dominant *weak* incumbent is
    # the displaceable case we actively want to surface.
    conc = row["hhi_us"] or 0
    rating = row["leader_avg_rating"] or 0
    if conc > 0.35 and rating >= 4.5:
        raw *= 1 - min((conc - 0.35) * 0.55, 0.30)

    return round(raw, 1)


def main():
    enriched = json.loads((NICHE_DIR / "enriched.json").read_text())
    ads, queried = load_ads()
    apps = list(enriched.values())

    groups = defaultdict(list)
    for a in apps:
        groups[(a["family"], a["sub_niche"])].append(a)

    rows = []
    for (family, label), members in groups.items():
        if len(members) < 3:
            continue
        row = analyse(members, family, label, ads, queried)
        row["score"] = score(row)
        rows.append(row)

    rows.sort(key=lambda r: (r["low_volume"], -r["score"]))

    (NICHE_DIR / "opportunities.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False))
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    (DASHBOARD_DIR / "niches.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False))

    solid = [r for r in rows if not r["low_volume"]]
    print(f"{'sub-niche':34s} {'family':22s} {'apps':>5s} {'USdl':>10s} "
          f"{'$/dl':>6s} {'rat':>5s} {'stl':>4s} {'UA%':>5s} {'score':>6s}")
    for r in solid[:45]:
        ua = r["ua_advertiser_share"]
        print(f"{r['sub_niche'][:33]:34s} {r['family'][:21]:22s} "
              f"{r['apps_with_downloads']:5d} {r['us_downloads_12m']:10,} "
              f"{r['us_rpd_smoothed']:6.2f} {(r['leader_avg_rating'] or 0):5.2f} "
              f"{r['leaders_stale_9m']:4d} "
              f"{(f'{ua*100:.0f}%' if ua is not None else '—'):>5s} "
              f"{r['score']:6.1f}")
    print(f"\n{len(solid)} measurable sub-niches, "
          f"{len(rows) - len(solid)} below {MIN_VOLUME:,} US downloads.")

    REPORT_DIR.mkdir(exist_ok=True)
    out = REPORT_DIR / f"opportunity_scan_{datetime.now():%Y%m%d}.md"
    write_report(out, rows)
    print(f"Report: {out}")


def write_report(path, rows):
    L = [f"# US iOS niche opportunity scan — {datetime.now():%Y-%m-%d}\n"]
    L.append("Market: **US**, iOS only, trailing 12 months, iPhone + iPad.\n")
    L.append("`$/dl` is revenue per download, shrunk toward zero on small "
             "samples. **Ad revenue is excluded** — the API reports IAP and paid "
             "only — so rows flagged `ads?` are under-measured.\n")
    L.append("`UA%` is the share of sampled leaders running paid user "
             "acquisition. High UA means installs are bought, not earned.\n")

    solid = [r for r in rows if not r["low_volume"]]
    L.append("\n## Ranked sub-niches\n")
    L.append("| # | Sub-niche | Family | Live apps | US dl | $/dl | Leader ★ | Stale | UA% | Ads? | Score |")
    L.append("|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|")
    for i, r in enumerate(solid, 1):
        ua = r["ua_advertiser_share"]
        L.append(
            f"| {i} | {r['sub_niche']} | {r['family']} | {r['apps_with_downloads']} | "
            f"{r['us_downloads_12m']:,} | ${r['us_rpd_smoothed']:.2f} | "
            f"{r['leader_avg_rating'] or '—'} | {r['leaders_stale_9m']}/5 | "
            f"{f'{ua*100:.0f}%' if ua is not None else '—'} | "
            f"{'yes' if r['ads_caveat'] else '—'} | **{r['score']}** |")

    L.append("\n## Detail\n")
    for r in solid:
        L.append(f"\n### {r['sub_niche']} — {r['family']}  ·  score {r['score']}\n")
        ua = r["ua_advertiser_share"]
        L.append(
            f"{r['apps_total']} apps matched, {r['apps_with_downloads']} with "
            f"measurable downloads. HHI {r['hhi_us']}. {r['paid_apps']} paid, "
            f"{r['iap_apps']} with IAP, {r['ad_funded_apps']} likely ad-funded "
            f"({r['ad_funded_download_share']*100:.0f}% of downloads). "
            f"Paid UA: {r['ua_advertisers']}/{r['ua_sampled']} sampled leaders"
            f"{f' ({ua*100:.0f}%)' if ua is not None else ''}, "
            f"total SoV {r['ua_total_sov']}. "
            f"US is {r['us_share_of_ww_rev']*100:.0f}% of worldwide revenue.\n")
        L.append("| App | Publisher | US dl | US rev | ★ | Ratings | Updated | UA SoV |")
        L.append("|---|---|---:|---:|---:|---:|---|---:|")
        for a in r["leaders"]:
            sov = a["ua_sov"]
            L.append(
                f"| {a['name']} | {a['publisher']} | {a['us_downloads_12m']:,} | "
                f"${a['us_revenue_12m']:,.0f} | {a['rating'] or '—'} | "
                f"{a['global_rating_count'] or 0:,} | {a['updated_date']} "
                f"({a['days_since_update']}d) | "
                f"{f'{sov:.4f}' if sov else '—'} |")

    thin = [r["sub_niche"] for r in rows if r["low_volume"]]
    if thin:
        L.append(f"\n## Below {MIN_VOLUME:,} US downloads — not measurable\n")
        L.append(", ".join(thin) + "\n")

    path.write_text("\n".join(L))


if __name__ == "__main__":
    main()
