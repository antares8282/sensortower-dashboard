"""Overview page — KPI cards, category charts, top revenue leaders."""
import streamlit as st
from components.data_loader import load_category_summary, load_app_details, load_metadata
from components.formatters import fmt_money, fmt_number, fmt_rating
from components.charts import revenue_by_category_bar, downloads_by_category_bar, top_apps_revenue_bar


def render():
    st.title("Market Overview")

    cat_summary = load_category_summary()
    app_details = load_app_details()
    meta = load_metadata()

    # ---- KPI Row ----
    total_apps = len(app_details)
    total_revenue = sum(c["grossing_revenue"] for c in cat_summary.values())
    total_downloads = sum(c["grossing_downloads"] for c in cat_summary.values())
    avg_rating = sum(c["avg_rating"] for c in cat_summary.values()) / max(len(cat_summary), 1)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Apps Tracked", total_apps)
    k2.metric("Est. Monthly Revenue", fmt_money(total_revenue))
    k3.metric("Est. Monthly Downloads", fmt_number(total_downloads))
    k4.metric("Avg. Rating", fmt_rating(avg_rating))
    k5.metric("Categories", len(cat_summary))

    st.divider()

    # ---- Category Charts ----
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Category")
        st.caption("Top Grossing apps, estimated monthly revenue")
        fig = revenue_by_category_bar(cat_summary)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Downloads by Category")
        st.caption("Top Grossing apps, estimated monthly downloads")
        fig = downloads_by_category_bar(cat_summary)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---- Category Summary Table ----
    st.subheader("Category Performance")

    cat_rows = []
    for name, data in cat_summary.items():
        cat_rows.append({
            "Category": name,
            "Revenue": fmt_money(data["grossing_revenue"]),
            "Downloads": fmt_number(data["grossing_downloads"]),
            "Rev/Download": fmt_money(data["revenue_per_download"]),
            "Avg Rating": fmt_rating(data["avg_rating"]),
            "Apps": data["total_apps_tracked"],
        })

    st.dataframe(
        cat_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Category": st.column_config.TextColumn(width="medium"),
            "Revenue": st.column_config.TextColumn(width="small"),
            "Downloads": st.column_config.TextColumn(width="small"),
        },
    )

    st.divider()

    # ---- Top 15 Revenue Leaders ----
    st.subheader("Top 15 Revenue Leaders")

    all_apps = list(app_details.values())
    all_apps.sort(key=lambda x: x.get("revenue", 0), reverse=True)

    fig = top_apps_revenue_bar(all_apps, n=15)
    st.plotly_chart(fig, use_container_width=True)

    # Also as a table
    top_rows = []
    for i, app in enumerate(all_apps[:15], 1):
        top_rows.append({
            "#": i,
            "App": app["name"],
            "Publisher": app["publisher_name"],
            "Revenue": fmt_money(app.get("revenue", 0)),
            "Downloads": fmt_number(app.get("downloads", 0)),
            "Rating": fmt_rating(app.get("rating", 0)),
        })

    st.dataframe(top_rows, use_container_width=True, hide_index=True)
