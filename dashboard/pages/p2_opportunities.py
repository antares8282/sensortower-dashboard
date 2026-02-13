"""Opportunities page — Apps not updated in 1+ year with review data."""
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from components.data_loader import load_all_apps_table, load_app_details
from components.formatters import fmt_money, fmt_number, fmt_rating

PERIOD_MAP = {
    "Last Month": ("downloads_1m", "revenue_1m"),
    "Last 3 Months": ("downloads_3m", "revenue_3m"),
    "Last 6 Months": ("downloads_6m", "revenue_6m"),
}


def get_period_label(base_label, selected_period):
    """Generate dynamic column header: 'Downloads Last Month'"""
    period_suffix = selected_period.replace("Last ", "")
    return f"{base_label} {period_suffix}"


def render():
    st.title("Opportunities")

    apps = load_all_apps_table()
    app_details = load_app_details()  # For review counts

    if not apps:
        st.warning("No data available. Run data refresh first.")
        return

    # ---- Sidebar Filters (same as rankings) ----
    all_categories = sorted({a["category"] for a in apps})
    all_chart_types = sorted({a["chart_type"] for a in apps})

    selected_categories = st.sidebar.multiselect(
        "Category", all_categories, placeholder="All categories"
    )
    chart_options = ["All"] + all_chart_types
    selected_chart = st.sidebar.selectbox("Chart Type", chart_options)

    st.sidebar.divider()
    selected_period = st.sidebar.selectbox("Period", list(PERIOD_MAP.keys()))
    dl_field, rev_field = PERIOD_MAP[selected_period]

    # Filter by category and chart type
    filtered = apps
    if selected_categories:
        filtered = [a for a in filtered if a["category"] in selected_categories]
    if selected_chart != "All":
        filtered = [a for a in filtered if a["chart_type"] == selected_chart]

    # Filter stale apps (1+ year)
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    stale_apps = [
        a for a in filtered
        if a.get("updated_date") and a["updated_date"][:10] <= one_year_ago
    ]

    if not stale_apps:
        st.info("No apps found that haven't been updated in 1+ year.")
        return

    # Enrich with review count from app_details
    for app in stale_apps:
        app_id = str(app["app_id"])
        detail = app_details.get(app_id, {})
        app["review_count"] = detail.get("rating_count", 0)

    # Sort by downloads
    stale_sorted = sorted(stale_apps, key=lambda x: (x.get(dl_field) or 0), reverse=True)

    st.caption(
        f"{len(stale_sorted)} apps not updated for 1+ year — "
        f"high traffic + outdated = disruption opportunity"
    )

    # Dynamic headers
    dl_header = get_period_label("Downloads", selected_period)
    rev_header = get_period_label("Revenue", selected_period)

    # Build table
    rows = []
    for a in stale_sorted[:100]:  # Show top 100
        rows.append({
            "App": a["name"],
            "Publisher": a["publisher_name"],
            "Category": a["category"],
            "Rating": fmt_rating(a.get("rating", 0)),
            "Reviews": fmt_number(a.get("review_count", 0)),
            dl_header: fmt_number(a.get(dl_field, 0) or 0),
            rev_header: fmt_money(a.get(rev_field, 0) or 0),
            "Last Updated": (a.get("updated_date") or "")[:10],
        })
    df_opp = pd.DataFrame(rows)

    opp_event = st.dataframe(
        df_opp,
        use_container_width=True,
        hide_index=True,
        height=600,
        on_select="rerun",
        selection_mode="single-row",
        key="opp_table",
    )

    if opp_event and opp_event.selection and opp_event.selection.rows:
        row_idx = opp_event.selection.rows[0]
        st.session_state.selected_app_id = stale_sorted[row_idx]["app_id"]
        st.rerun()
