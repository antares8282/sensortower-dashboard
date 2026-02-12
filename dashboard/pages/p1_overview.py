"""Overview page — Rankings + Opportunities tabs with clickable rows."""
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from components.data_loader import load_all_apps_table
from components.formatters import fmt_money, fmt_number, fmt_rating

PERIOD_MAP = {
    "Last Month": ("downloads_1m", "revenue_1m"),
    "Last 3 Months": ("downloads_3m", "revenue_3m"),
    "Last 6 Months": ("downloads_6m", "revenue_6m"),
}


def render():
    st.title("App Rankings")

    apps = load_all_apps_table()
    if not apps:
        st.warning("No data available. Run data refresh first.")
        return

    # ---- Sidebar Filters ----
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

    # Filter
    filtered = apps
    if selected_categories:
        filtered = [a for a in filtered if a["category"] in selected_categories]
    if selected_chart != "All":
        filtered = [a for a in filtered if a["chart_type"] == selected_chart]

    if not filtered:
        st.info("No apps match the selected filters.")
        return

    # ---- Tabs ----
    tab1, tab2 = st.tabs(["Rankings", "Opportunities"])

    # ========== TAB 1: Rankings ==========
    with tab1:
        st.caption(f"Showing {min(len(filtered), 50)} of {len(filtered)} apps — click a row to view details")

        def build_ranking_df(sorted_apps):
            rows = []
            for i, a in enumerate(sorted_apps[:50], 1):
                rows.append({
                    "#": i,
                    "App": a["name"],
                    "Publisher": a["publisher_name"],
                    "Category": a["category"],
                    "Downloads": fmt_number(a.get(dl_field, 0) or 0),
                    "Revenue": fmt_money(a.get(rev_field, 0) or 0),
                })
            return pd.DataFrame(rows)

        # Table 1: By Downloads
        st.subheader("Top by Downloads")
        by_downloads = sorted(filtered, key=lambda x: (x.get(dl_field) or 0), reverse=True)
        df_dl = build_ranking_df(by_downloads)

        dl_event = st.dataframe(
            df_dl,
            use_container_width=True,
            hide_index=True,
            height=420,
            on_select="rerun",
            selection_mode="single-row",
            key="dl_table",
        )

        if dl_event and dl_event.selection and dl_event.selection.rows:
            row_idx = dl_event.selection.rows[0]
            st.session_state.selected_app_id = by_downloads[row_idx]["app_id"]
            st.rerun()

        st.divider()

        # Table 2: By Revenue
        st.subheader("Top by Revenue")
        by_revenue = sorted(filtered, key=lambda x: (x.get(rev_field) or 0), reverse=True)
        df_rev = build_ranking_df(by_revenue)

        rev_event = st.dataframe(
            df_rev,
            use_container_width=True,
            hide_index=True,
            height=420,
            on_select="rerun",
            selection_mode="single-row",
            key="rev_table",
        )

        if rev_event and rev_event.selection and rev_event.selection.rows:
            row_idx = rev_event.selection.rows[0]
            st.session_state.selected_app_id = by_revenue[row_idx]["app_id"]
            st.rerun()

    # ========== TAB 2: Opportunities ==========
    with tab2:
        one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        stale_apps = [
            a for a in filtered
            if a.get("updated_date")
            and a["updated_date"][:10] <= one_year_ago
        ]

        if not stale_apps:
            st.info("No stale apps found (all apps updated within the last year).")
        else:
            stale_sorted = sorted(stale_apps, key=lambda x: (x.get(dl_field) or 0), reverse=True)
            st.caption(
                f"{len(stale_sorted)} apps not updated for 1+ year — "
                f"high traffic + outdated = disruption opportunity"
            )

            rows = []
            for i, a in enumerate(stale_sorted[:50], 1):
                rows.append({
                    "#": i,
                    "App": a["name"],
                    "Publisher": a["publisher_name"],
                    "Category": a["category"],
                    "Rating": fmt_rating(a.get("rating", 0)),
                    "Downloads": fmt_number(a.get(dl_field, 0) or 0),
                    "Revenue": fmt_money(a.get(rev_field, 0) or 0),
                    "Last Updated": (a.get("updated_date") or "")[:10],
                    "Age (yrs)": round(a.get("app_age_years") or 0, 1),
                })
            df_opp = pd.DataFrame(rows)

            opp_event = st.dataframe(
                df_opp,
                use_container_width=True,
                hide_index=True,
                height=500,
                on_select="rerun",
                selection_mode="single-row",
                key="opp_table",
            )

            if opp_event and opp_event.selection and opp_event.selection.rows:
                row_idx = opp_event.selection.rows[0]
                st.session_state.selected_app_id = stale_sorted[row_idx]["app_id"]
                st.rerun()
