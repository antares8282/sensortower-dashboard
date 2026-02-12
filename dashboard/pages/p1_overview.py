"""Overview page — two filterable tables: by downloads & by revenue."""
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
        "Category", all_categories, default=all_categories
    )
    selected_charts = st.sidebar.multiselect(
        "Chart Type", all_chart_types, default=all_chart_types
    )

    # Filter
    filtered = [
        a for a in apps
        if a["category"] in selected_categories
        and a["chart_type"] in selected_charts
    ]

    if not filtered:
        st.info("No apps match the selected filters.")
        return

    st.caption(f"Showing {len(filtered)} apps")

    # ---- Helper to build table rows ----
    def build_rows(sorted_apps):
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
                "Age (yrs)": round(a.get("app_age_years", 0), 1),
                "Released": (a.get("release_date") or "")[:10],
                "Updated": (a.get("updated_date") or "")[:10],
                "IAP": "Yes" if a.get("has_iap") else "No",
            })
        return rows

    # ---- Table 1: By Downloads ----
    st.subheader("Top by Downloads")
    by_downloads = sorted(filtered, key=lambda x: x.get("downloads", 0), reverse=True)
    st.dataframe(build_rows(by_downloads), use_container_width=True, hide_index=True, height=420)

    # App selector for downloads table
    dl_names = [f"{a['name']} — {a['publisher_name']}" for a in by_downloads]
    dl_selected = st.selectbox("Select app to view details", dl_names, key="dl_select", index=None, placeholder="Pick an app...")
    if dl_selected and st.button("View Details →", key="dl_btn"):
        idx = dl_names.index(dl_selected)
        st.session_state.selected_app_id = by_downloads[idx]["app_id"]
        st.rerun()

    st.divider()

    # ---- Table 2: By Revenue ----
    st.subheader("Top by Revenue")
    by_revenue = sorted(filtered, key=lambda x: x.get("revenue", 0), reverse=True)
    st.dataframe(build_rows(by_revenue), use_container_width=True, hide_index=True, height=420)

    # App selector for revenue table
    rev_names = [f"{a['name']} — {a['publisher_name']}" for a in by_revenue]
    rev_selected = st.selectbox("Select app to view details", rev_names, key="rev_select", index=None, placeholder="Pick an app...")
    if rev_selected and st.button("View Details →", key="rev_btn"):
        idx = rev_names.index(rev_selected)
        st.session_state.selected_app_id = by_revenue[idx]["app_id"]
        st.rerun()
