"""
Opportunities — niche-level, not app-level.

The original version listed individual stale apps from the US top-50 charts,
which could not find underserved niches: wrong unit (an app, not a market), and
top-chart data is survivorship-biased by construction — an underserved niche is
precisely one where nobody charted.

Reads dashboard_data/current/niches.json, produced by the niche pipeline
(search_entities catalog sweep → membership confirmation → sales estimates →
ad-intel sampling), which reaches apps that never chart.
"""
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "dashboard_data"


@st.cache_data(ttl=300)
def load_niches():
    path = DATA_DIR / "current" / "niches.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def scatter(rows):
    """
    Money against paid-UA pressure. The useful region is bottom-right: a niche
    that monetizes while its leaders are *not* buying installs, which is where
    an organic launch can still land.
    """
    pts = [r for r in rows if r["ua_advertiser_share"] is not None]
    if not pts:
        return None

    x = [r["ua_advertiser_share"] * 100 for r in pts]
    y = [min(r["us_rpd_smoothed"], 30) for r in pts]
    size = [max(9, min(42, (r["us_downloads_12m"] / 70000) + 9)) for r in pts]
    color = ["#E8925A" if r["ads_caveat"] else "#4FB7C2" for r in pts]

    fig = go.Figure()
    fig.add_vrect(x0=0, x1=35, fillcolor="#4FB7C2", opacity=0.07, line_width=0)
    fig.add_vline(x=35, line_dash="dot", line_color="#666", line_width=1)

    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers+text",
        text=[r["sub_niche"] for r in pts],
        textposition="top center", textfont=dict(size=9, color="#9AA"),
        marker=dict(size=size, color=color, opacity=0.82,
                    line=dict(width=1, color="#0E1117")),
        hovertemplate=[
            f"<b>{r['sub_niche']}</b><br>{r['family']}<br>"
            f"US downloads: {r['us_downloads_12m']:,}<br>"
            f"Revenue/download: ${r['us_rpd_smoothed']:.2f}<br>"
            f"Leaders advertising: {r['ua_advertisers']}/{r['ua_sampled']}<br>"
            f"Live apps: {r['apps_with_downloads']}<br>"
            f"Score: {r['score']}<extra></extra>"
            for r in pts
        ],
    ))
    fig.update_layout(
        height=520, margin=dict(l=10, r=10, t=34, b=10),
        xaxis=dict(title="← share of leaders buying installs (paid UA)",
                   range=[-4, 104], gridcolor="#222", ticksuffix="%"),
        yaxis=dict(title="revenue per download →", gridcolor="#222",
                   tickprefix="$"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        annotations=[dict(x=3, y=max(y) * 0.96, xref="x", yref="y",
                          text="pays, and not ad-gated", showarrow=False,
                          xanchor="left",
                          font=dict(size=10, color="#4FB7C2"))],
    )
    return fig


def render():
    st.title("Opportunities")

    rows = load_niches()
    if not rows:
        st.warning(
            "No niche data yet. Run:\n\n"
            "`python scripts/niche_scan.py` → `niche_filter.py` → "
            "`niche_enrich.py` → `niche_ads.py` → `niche_opportunity.py`"
        )
        return

    st.caption(
        "US market · iOS · trailing 12 months. Sub-niches are built from keyword "
        "sweeps of the full catalog, so apps that never chart are included."
    )

    # ---- filters ----
    families = sorted({r["family"] for r in rows})
    sel_fam = st.sidebar.multiselect("Family", families, placeholder="All families")
    show_thin = st.sidebar.checkbox(
        "Show low-volume niches", value=False,
        help="Under 10,000 US downloads/yr — revenue per download is not "
             "trustworthy at that sample size.",
    )
    max_ua = st.sidebar.slider(
        "Max % of leaders running paid ads", 0, 100, 100,
        help="Lower this to find niches where installs are still earned "
             "organically rather than bought.",
    )
    min_rpd = st.sidebar.slider("Min revenue per download ($)", 0.0, 20.0, 0.0, 0.5)

    view = rows
    if sel_fam:
        view = [r for r in view if r["family"] in sel_fam]
    if not show_thin:
        view = [r for r in view if not r["low_volume"]]
    view = [r for r in view if r["us_rpd_smoothed"] >= min_rpd]
    view = [r for r in view
            if r["ua_advertiser_share"] is None
            or r["ua_advertiser_share"] * 100 <= max_ua]

    if not view:
        st.info("No niches match those filters.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sub-niches", len(view))
    c2.metric("Apps covered", f"{sum(r['apps_total'] for r in view):,}")
    c3.metric("US downloads 12m", f"{sum(r['us_downloads_12m'] for r in view):,}")
    c4.metric("US revenue 12m", f"${sum(r['us_revenue_12m'] for r in view):,.0f}")

    fig = scatter(view)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    df = pd.DataFrame([{
        "Sub-niche": r["sub_niche"],
        "Family": r["family"],
        "Live apps": r["apps_with_downloads"],
        "US downloads": r["us_downloads_12m"],
        "$/download": r["us_rpd_smoothed"],
        "Leader ★": r["leader_avg_rating"],
        "Stale": r["leaders_stale_9m"],
        "Paid UA": (r["ua_advertiser_share"] * 100
                    if r["ua_advertiser_share"] is not None else None),
        "Ads?": "yes" if r["ads_caveat"] else "",
        "Score": r["score"],
    } for r in view])

    event = st.dataframe(
        df, use_container_width=True, hide_index=True, height=440,
        on_select="rerun", selection_mode="single-row", key="niche_table",
        column_config={
            "US downloads": st.column_config.NumberColumn(format="%d"),
            "$/download": st.column_config.NumberColumn(
                format="$%.2f",
                help="Revenue per download, shrunk toward zero on small samples. "
                     "Excludes ad revenue, which this API does not report.",
            ),
            "Stale": st.column_config.NumberColumn(
                format="%d/5", help="Top-5 apps with no release in 9+ months."),
            "Paid UA": st.column_config.NumberColumn(
                format="%.0f%%",
                help="Share of sampled leaders running paid user acquisition. "
                     "High means installs are bought, not earned."),
            "Score": st.column_config.ProgressColumn(
                format="%.0f", min_value=0, max_value=100),
        },
    )

    # ---- drill-down ----
    if event and event.selection and event.selection.rows:
        r = view[event.selection.rows[0]]
        st.divider()
        st.subheader(r["sub_niche"])
        st.caption(r["family"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("US downloads 12m", f"{r['us_downloads_12m']:,}")
        m2.metric("US revenue 12m", f"${r['us_revenue_12m']:,.0f}")
        m3.metric("Revenue / download", f"${r['us_rpd_smoothed']:.2f}")
        m4.metric("Live competitors", r["apps_with_downloads"])

        if r["ua_sampled"]:
            share = r["ua_advertiser_share"] * 100
            verdict = ("installs are largely bought here — organic entry is hard"
                       if share >= 60 else
                       "mixed; some paid pressure" if share >= 35 else
                       "little paid UA — organic and ASO can still win")
            st.markdown(
                f"**Paid user acquisition** — {r['ua_advertisers']} of "
                f"{r['ua_sampled']} sampled leaders are advertising "
                f"({share:.0f}%), total share of voice {r['ua_total_sov']}. "
                f"*{verdict}.*"
            )
        else:
            st.caption("No ad-intel sample for this niche.")

        if r["ads_caveat"]:
            st.warning(
                f"{r['ad_funded_apps']} apps here are free with no IAP and carry "
                f"{r['ad_funded_download_share']*100:.0f}% of downloads — almost "
                "certainly ad-funded, and that revenue is invisible to this API. "
                "Treat the revenue figure as a floor."
            )

        conc = r["hhi_us"]
        if conc is not None:
            shape = ("one player owns it" if conc > 0.25
                     else "fragmented — no dominant incumbent" if conc < 0.10
                     else "moderately concentrated")
            st.caption(
                f"Concentration HHI {conc} — {shape}. {r['paid_apps']} paid, "
                f"{r['iap_apps']} with IAP. US is "
                f"{r['us_share_of_ww_rev']*100:.0f}% of worldwide revenue."
            )

        st.markdown("**Leading apps**")
        st.dataframe(
            pd.DataFrame([{
                "App": a["name"],
                "Publisher": a["publisher"],
                "US downloads": a["us_downloads_12m"],
                "US revenue": a["us_revenue_12m"],
                "★": a["rating"],
                "Ratings": a["global_rating_count"],
                "Last update": a["updated_date"],
                "Days stale": a["days_since_update"],
                "Ad SoV": a["ua_sov"],
            } for a in r["leaders"]]),
            use_container_width=True, hide_index=True,
            column_config={
                "US downloads": st.column_config.NumberColumn(format="%d"),
                "US revenue": st.column_config.NumberColumn(format="$%d"),
                "Ratings": st.column_config.NumberColumn(format="%d"),
                "★": st.column_config.NumberColumn(format="%.2f"),
                "Ad SoV": st.column_config.NumberColumn(format="%.4f"),
            },
        )
