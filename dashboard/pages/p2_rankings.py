"""Rankings page — category & chart type filters, ranked table."""
import streamlit as st
from components.data_loader import load_rankings
from components.formatters import fmt_money, fmt_number, fmt_rating, CHART_TYPE_LABELS


def render():
    st.title("App Rankings")

    rankings = load_rankings()

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox(
            "Category",
            list(rankings.keys()),
            index=0,
        )
    with col2:
        chart_options = list(rankings.get(category, {}).keys())
        chart_labels = [CHART_TYPE_LABELS.get(c, c) for c in chart_options]
        chart_type_label = st.selectbox("Chart Type", chart_labels, index=0)
        chart_type = chart_options[chart_labels.index(chart_type_label)] if chart_labels else ""

    st.divider()

    # Ranked table
    chart_data = rankings.get(category, {}).get(chart_type, {})
    apps = chart_data.get("apps", [])
    date = chart_data.get("date", "")[:10]

    if date:
        st.caption(f"Data from: {date} • Country: {chart_data.get('country', 'US')}")

    if not apps:
        st.warning("No ranking data available for this selection.")
        return

    # Build display table
    rows = []
    for app in apps:
        rows.append({
            "Rank": app["rank"],
            "App": app["name"],
            "Publisher": app["publisher_name"],
            "Rating": fmt_rating(app.get("rating", 0)),
            "Revenue": fmt_money(app.get("revenue", 0)),
            "Downloads": fmt_number(app.get("downloads", 0)),
            "IAP": "✅" if app.get("has_iap") else "❌",
            "Price": f"${app['price']:.2f}" if app.get("price", 0) > 0 else "Free",
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        height=min(len(rows) * 38 + 40, 750),
        column_config={
            "Rank": st.column_config.NumberColumn(width="tiny"),
            "App": st.column_config.TextColumn(width="large"),
            "Publisher": st.column_config.TextColumn(width="medium"),
        },
    )

    # Summary stats
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    total_rev = sum(a.get("revenue", 0) for a in apps)
    total_dl = sum(a.get("downloads", 0) for a in apps)
    avg_rating = sum(a.get("rating", 0) for a in apps if a.get("rating", 0) > 0) / max(
        sum(1 for a in apps if a.get("rating", 0) > 0), 1
    )
    iap_pct = sum(1 for a in apps if a.get("has_iap")) / max(len(apps), 1) * 100

    c1.metric("Total Revenue", fmt_money(total_rev))
    c2.metric("Total Downloads", fmt_number(total_dl))
    c3.metric("Avg Rating", fmt_rating(avg_rating))
    c4.metric("IAP Adoption", f"{iap_pct:.0f}%")

    # Download CSV
    st.download_button(
        "📥 Download as CSV",
        data=_to_csv(rows),
        file_name=f"rankings_{category}_{chart_type}.csv",
        mime="text/csv",
    )


def _to_csv(rows):
    if not rows:
        return ""
    import csv
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
