"""
Opportunities — niche-level, not app-level.

The previous version listed individual stale apps from the US top-50 charts.
That could not answer "which niche is underserved" for two reasons: it worked
on the wrong unit (an app, not a market), and its data was survivorship-biased
by construction — top-chart apps are the winners, and an underserved niche is
precisely one where nobody has charted.

This version reads dashboard_data/current/niches.json, built by the niche
pipeline (search_entities → keyword confirmation → sales estimates), which
reaches apps that never chart.
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
    Market vs buildability. This chart exists to make one thing unmissable:
    the best-paying niches are usually the least buildable, because the barrier
    IS the reason they stay underserved. The top-right quadrant is the only
    place worth starting.
    """
    x = [r["buildability"] for r in rows]
    y = [r["market_score"] for r in rows]
    size = [max(8, min(40, (r["us_downloads_12m"] / 60000) + 8)) for r in rows]
    color = ["#FF6B6B" if r["ads_caveat"] else "#4FB7C2" for r in rows]
    text = [r["sub_niche"] for r in rows]
    hover = [
        f"<b>{r['sub_niche']}</b><br>"
        f"US downloads 12m: {r['us_downloads_12m']:,}<br>"
        f"Revenue/download: ${r['us_rpd_smoothed']:.2f}<br>"
        f"Live apps: {r['apps_with_downloads']}<br>"
        f"Leader rating: {r['leader_avg_rating'] or '—'}<br>"
        f"GO score: {r['go_score']}<extra></extra>"
        for r in rows
    ]

    fig = go.Figure()
    mx, my = 62, 55  # quadrant dividers, drawn before points so dots sit on top
    fig.add_vrect(x0=mx, x1=100, fillcolor="#4FB7C2", opacity=0.06, line_width=0)
    fig.add_hrect(y0=my, y1=100, fillcolor="#4FB7C2", opacity=0.06, line_width=0)
    fig.add_vline(x=mx, line_dash="dot", line_color="#666", line_width=1)
    fig.add_hline(y=my, line_dash="dot", line_color="#666", line_width=1)

    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers+text", text=text,
        textposition="top center", textfont=dict(size=9, color="#AAA"),
        marker=dict(size=size, color=color, opacity=0.8,
                    line=dict(width=1, color="#0E1117")),
        hovertemplate=hover,
    ))
    fig.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(title="Buildability →  (higher = shippable by a small team)",
                   range=[30, 105], gridcolor="#222"),
        yaxis=dict(title="Market score →", range=[0, 100], gridcolor="#222"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        annotations=[dict(
            x=97, y=97, xref="x", yref="y", text="build here",
            showarrow=False, font=dict(size=10, color="#4FB7C2"),
        )],
    )
    return fig


def render():
    st.title("Opportunities")

    rows = load_niches()
    if not rows:
        st.warning(
            "No niche data yet. Run the pipeline:\n\n"
            "`python scripts/niche_scan.py` → `niche_filter.py` → "
            "`niche_enrich.py` → `niche_opportunity.py`"
        )
        return

    st.caption(
        "US market · iOS · trailing 12 months. Sub-niches are built from keyword "
        "sweeps of the full catalog, so apps that never chart are included."
    )

    # ---- filters ----
    parents = sorted({r["niche"] for r in rows})
    sel_parent = st.sidebar.multiselect(
        "Niche family", parents, placeholder="All families"
    )
    show_thin = st.sidebar.checkbox(
        "Show low-volume niches", value=False,
        help="Under 10,000 US downloads/yr — revenue-per-download is not "
             "trustworthy at that sample size.",
    )
    min_build = st.sidebar.slider(
        "Minimum buildability", 0, 100, 0,
        help="Higher = fewer data moats, hardware dependencies, network effects "
             "and regulatory barriers.",
    )

    view = rows
    if sel_parent:
        view = [r for r in view if r["niche"] in sel_parent]
    if not show_thin:
        view = [r for r in view if not r["low_volume"]]
    view = [r for r in view if (r["buildability"] or 0) >= min_build]

    if not view:
        st.info("No niches match those filters.")
        return

    # ---- the tension, stated once ----
    st.info(
        "**Buildability and opportunity pull against each other.** The moat is "
        "usually *why* a niche stays underserved — Navionics earns $23M rated "
        "2.86★ because charts need licensed hydrographic data, not better code. "
        "Qibla finders are trivially buildable, which is why 55 exist and revenue "
        "is $0.37/download. Look for niches gated by effort, not by data."
    )

    st.plotly_chart(scatter(view), use_container_width=True)

    # ---- table ----
    df = pd.DataFrame([{
        "Sub-niche": r["sub_niche"],
        "Family": r["niche"],
        "Live apps": r["apps_with_downloads"],
        "US downloads": r["us_downloads_12m"],
        "$/download": r["us_rpd_smoothed"],
        "Leader ★": r["leader_avg_rating"],
        "Stale leaders": r["leaders_stale_9m"],
        "Ads?": "yes" if r["ads_caveat"] else "",
        "Market": r["market_score"],
        "Build": r["buildability"],
        "GO": r["go_score"],
    } for r in view])

    event = st.dataframe(
        df, use_container_width=True, hide_index=True, height=430,
        on_select="rerun", selection_mode="single-row", key="niche_table",
        column_config={
            "US downloads": st.column_config.NumberColumn(format="%d"),
            "$/download": st.column_config.NumberColumn(
                format="$%.2f",
                help="Revenue per download, shrunk toward zero on small samples. "
                     "Excludes ad revenue, which this API does not report.",
            ),
            "Stale leaders": st.column_config.NumberColumn(
                format="%d/5", help="Top-5 apps with no release in 9+ months."
            ),
            "Market": st.column_config.ProgressColumn(
                format="%.0f", min_value=0, max_value=100
            ),
            "Build": st.column_config.ProgressColumn(
                format="%.0f", min_value=0, max_value=100
            ),
            "GO": st.column_config.ProgressColumn(
                format="%.0f", min_value=0, max_value=100,
                help="Geometric mean of Market and Build — a niche must clear both.",
            ),
        },
    )

    # ---- drill-down ----
    if event and event.selection and event.selection.rows:
        r = view[event.selection.rows[0]]
        st.divider()
        st.subheader(r["sub_niche"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("US downloads 12m", f"{r['us_downloads_12m']:,}")
        c2.metric("US revenue 12m", f"${r['us_revenue_12m']:,.0f}")
        c3.metric("Revenue / download", f"${r['us_rpd_smoothed']:.2f}")
        c4.metric("Live competitors", r["apps_with_downloads"])

        if r["barrier_note"]:
            barriers = ", ".join(r["top_barriers"]) or "no dominant barrier"
            st.markdown(f"**Build barriers** — *{barriers}*  \n{r['barrier_note']}")

        if r["ads_caveat"]:
            st.warning(
                f"{r['ad_funded_apps']} apps here are free with no IAP and carry "
                f"{r['ad_funded_download_share']*100:.0f}% of downloads — they are "
                "almost certainly ad-funded, and that revenue is invisible to this "
                "API. Treat the revenue figure as a floor."
            )

        conc = r["hhi_us"]
        if conc is not None:
            shape = ("one player owns it" if conc > 0.25
                     else "fragmented — no dominant incumbent" if conc < 0.10
                     else "moderately concentrated")
            st.caption(
                f"Concentration HHI {conc} — {shape}. "
                f"{r['paid_apps']} paid, {r['iap_apps']} with IAP. "
                f"US is {r['us_share_of_ww_rev']*100:.0f}% of worldwide revenue."
            )

        st.markdown("**Leading apps**")
        leaders = pd.DataFrame([{
            "App": a["name"],
            "Publisher": a["publisher"],
            "US downloads": a["us_downloads_12m"],
            "US revenue": a["us_revenue_12m"],
            "Rating": a["rating"],
            "Ratings": a["global_rating_count"],
            "Last update": a["updated_date"],
            "Days stale": a["days_since_update"],
        } for a in r["leaders"]])
        st.dataframe(
            leaders, use_container_width=True, hide_index=True,
            column_config={
                "US downloads": st.column_config.NumberColumn(format="%d"),
                "US revenue": st.column_config.NumberColumn(format="$%d"),
                "Ratings": st.column_config.NumberColumn(format="%d"),
                "Rating": st.column_config.NumberColumn(format="%.2f"),
            },
        )
