"""Publishers page — leaderboard table, revenue chart, treemap."""
import streamlit as st
from components.data_loader import load_publisher_summary
from components.formatters import fmt_money, fmt_number, fmt_rating
from components.charts import publisher_treemap


def render():
    st.title("Publisher Leaderboard")

    pub_summary = load_publisher_summary()

    if not pub_summary:
        st.warning("No publisher data available.")
        return

    # ---- KPI Row ----
    total_pubs = len(pub_summary)
    top_pub = pub_summary[0] if pub_summary else {}
    total_rev = sum(p.get("total_revenue", 0) for p in pub_summary)

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Publishers", total_pubs)
    k2.metric("Top Publisher", top_pub.get("publisher_name", "N/A"))
    k3.metric("Combined Revenue", fmt_money(total_rev))

    st.divider()

    # ---- Sort Options ----
    sort_by = st.selectbox(
        "Sort by",
        ["Chart Appearances", "Revenue", "Downloads", "App Count", "Avg Rating"],
        index=0,
    )

    sort_key = {
        "Chart Appearances": "chart_appearances",
        "Revenue": "total_revenue",
        "Downloads": "total_downloads",
        "App Count": "app_count",
        "Avg Rating": "avg_rating",
    }[sort_by]

    sorted_pubs = sorted(pub_summary, key=lambda x: x.get(sort_key, 0), reverse=True)

    # ---- Publisher Table ----
    rows = []
    for i, pub in enumerate(sorted_pubs[:50], 1):
        rows.append({
            "#": i,
            "Publisher": pub["publisher_name"],
            "Chart Appearances": pub.get("chart_appearances", 0),
            "Apps": pub.get("app_count", 0),
            "Revenue": fmt_money(pub.get("total_revenue", 0)),
            "Downloads": fmt_number(pub.get("total_downloads", 0)),
            "Avg Rating": fmt_rating(pub.get("avg_rating", 0)),
            "Top App": pub.get("top_app_name", ""),
            "Categories": ", ".join(pub.get("categories", [])[:3]),
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        height=min(len(rows) * 38 + 40, 750),
        column_config={
            "#": st.column_config.NumberColumn(width="tiny"),
            "Publisher": st.column_config.TextColumn(width="large"),
            "Top App": st.column_config.TextColumn(width="medium"),
        },
    )

    # ---- Treemap ----
    st.divider()
    st.subheader("Revenue Share (Top 20 Publishers)")

    fig = publisher_treemap(pub_summary, n=20)
    st.plotly_chart(fig, use_container_width=True)
