"""Trends page — time-series charts for revenue/downloads by category."""
import streamlit as st
from components.data_loader import load_trends, load_category_summary
from components.charts import trends_line_chart
from components.formatters import fmt_money, fmt_number


def render():
    st.title("Market Trends")

    trends = load_trends()
    dates = trends.get("dates", [])

    if len(dates) < 2:
        st.info(
            "📅 **Trends data is building up!**\n\n"
            "This page shows historical trends over time. "
            f"We currently have **{len(dates)} data point{'s' if len(dates) != 1 else ''}**. "
            "As the daily data refresh runs, this page will populate with trend charts.\n\n"
            "Check back after a few days of data collection!"
        )

        if len(dates) == 1:
            st.caption(f"First data point: {dates[0]}")

        # Show current snapshot as a preview
        st.divider()
        st.subheader("Current Snapshot")
        cat_summary = load_category_summary()

        for cat_name, data in trends.get("categories", {}).items():
            rev = data.get("grossing_revenue", [0])[-1] if data.get("grossing_revenue") else 0
            dl = data.get("grossing_downloads", [0])[-1] if data.get("grossing_downloads") else 0
            st.markdown(f"**{cat_name}**: Revenue {fmt_money(rev)} • Downloads {fmt_number(dl)}")

        return

    # ---- Full Trends View (2+ data points) ----
    metric = st.selectbox(
        "Metric",
        [
            ("grossing_revenue", "Grossing Revenue"),
            ("grossing_downloads", "Grossing Downloads"),
            ("free_downloads", "Free App Downloads"),
        ],
        format_func=lambda x: x[1],
    )

    st.divider()

    fig = trends_line_chart(trends, metric=metric[0])
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No trend data to display.")

    # ---- Summary Table ----
    st.divider()
    st.subheader("Trend Summary")

    categories = trends.get("categories", {})
    rows = []
    for cat_name, cat_data in categories.items():
        values = cat_data.get(metric[0], [])
        if len(values) >= 2:
            latest = values[-1]
            previous = values[-2]
            change = latest - previous
            change_pct = (change / previous * 100) if previous else 0
            rows.append({
                "Category": cat_name,
                "Latest": fmt_money(latest) if "revenue" in metric[0] else fmt_number(latest),
                "Previous": fmt_money(previous) if "revenue" in metric[0] else fmt_number(previous),
                "Change": f"{change_pct:+.1f}%",
            })

    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
