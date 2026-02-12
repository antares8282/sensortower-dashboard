"""Overview page — two clickable tables: by downloads & by revenue."""
import pandas as pd
import streamlit as st
from components.data_loader import load_all_apps_table
from components.formatters import fmt_money, fmt_number, fmt_rating


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

    # Filter
    filtered = apps
    if selected_categories:
        filtered = [a for a in filtered if a["category"] in selected_categories]
    if selected_chart != "All":
        filtered = [a for a in filtered if a["chart_type"] == selected_chart]

    if not filtered:
        st.info("No apps match the selected filters.")
        return

    st.caption(f"Showing {len(filtered)} apps — click a row to view details")

    # ---- Helper to build dataframe ----
    def build_df(sorted_apps):
        rows = []
        for i, a in enumerate(sorted_apps, 1):
            rows.append({
                "#": i,
                "App": a["name"],
                "Publisher": a["publisher_name"],
                "Category": a["category"],
                "Chart": a["chart_type"],
                "Rating": fmt_rating(a.get("rating", 0)),
                "Downloads": fmt_number(a.get("downloads", 0)),
                "Revenue": fmt_money(a.get("revenue", 0)),
                "Age (yrs)": round(a.get("app_age_years") or 0, 1),
                "Released": (a.get("release_date") or "")[:10],
                "Updated": (a.get("updated_date") or "")[:10],
                "IAP": "Yes" if a.get("has_iap") else "No",
            })
        return pd.DataFrame(rows)

    # ---- Table 1: By Downloads ----
    st.subheader("Top by Downloads")
    by_downloads = sorted(filtered, key=lambda x: x.get("downloads", 0), reverse=True)
    df_dl = build_df(by_downloads)

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

    # ---- Table 2: By Revenue ----
    st.subheader("Top by Revenue")
    by_revenue = sorted(filtered, key=lambda x: x.get("revenue", 0), reverse=True)
    df_rev = build_df(by_revenue)

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
