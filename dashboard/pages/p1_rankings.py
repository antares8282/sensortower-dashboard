"""Rankings page — side-by-side tables with dynamic column headers."""
import pandas as pd
import streamlit as st
from components.data_loader import load_all_apps_table
from components.formatters import fmt_money, fmt_number

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

    # Dynamic column headers
    dl_header = get_period_label("Downloads", selected_period)
    rev_header = get_period_label("Revenue", selected_period)

    st.caption(f"Showing top 50 of {len(filtered)} apps — click app name to view details")

    def build_ranking_df(sorted_apps):
        rows = []
        for a in sorted_apps[:50]:
            rows.append({
                "App": a["name"],
                "Publisher": a["publisher_name"],
                "Category": a["category"],
                dl_header: fmt_number(a.get(dl_field, 0) or 0),
                rev_header: fmt_money(a.get(rev_field, 0) or 0),
            })
        return pd.DataFrame(rows)

    # Two columns side-by-side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Downloads")
        by_downloads = sorted(filtered, key=lambda x: (x.get(dl_field) or 0), reverse=True)
        df_dl = build_ranking_df(by_downloads)

        dl_event = st.dataframe(
            df_dl,
            use_container_width=True,
            hide_index=True,
            height=600,
            on_select="rerun",
            selection_mode="single-row",
            key="dl_table",
        )

        if dl_event and dl_event.selection and dl_event.selection.rows:
            row_idx = dl_event.selection.rows[0]
            st.session_state.selected_app_id = by_downloads[row_idx]["app_id"]
            st.rerun()

    with col2:
        st.subheader("Top Grossing")
        by_revenue = sorted(filtered, key=lambda x: (x.get(rev_field) or 0), reverse=True)
        df_rev = build_ranking_df(by_revenue)

        rev_event = st.dataframe(
            df_rev,
            use_container_width=True,
            hide_index=True,
            height=600,
            on_select="rerun",
            selection_mode="single-row",
            key="rev_table",
        )

        if rev_event and rev_event.selection and rev_event.selection.rows:
            row_idx = rev_event.selection.rows[0]
            st.session_state.selected_app_id = by_revenue[row_idx]["app_id"]
            st.rerun()
