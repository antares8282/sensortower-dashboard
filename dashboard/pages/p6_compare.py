"""Compare page — side-by-side app comparison."""
import streamlit as st
from components.data_loader import load_app_details, get_all_apps_list
from components.formatters import fmt_money, fmt_number, fmt_rating
from components.charts import radar_chart


def render():
    st.title("App Comparison")

    app_details = load_app_details()
    apps_list = get_all_apps_list()

    if not apps_list:
        st.warning("No app data available.")
        return

    # Multi-select apps (2-5)
    app_names = [name for aid, name in apps_list]
    selected_names = st.multiselect(
        "Select 2-5 apps to compare",
        app_names,
        default=app_names[:3] if len(app_names) >= 3 else app_names[:2],
        max_selections=5,
    )

    if len(selected_names) < 2:
        st.info("Please select at least 2 apps to compare.")
        return

    # Find selected apps
    name_to_id = {name: aid for aid, name in apps_list}
    selected_apps = []
    for name in selected_names:
        aid = name_to_id.get(name)
        if aid:
            app = app_details.get(str(aid), {})
            if app:
                selected_apps.append(app)

    if len(selected_apps) < 2:
        st.warning("Could not find details for selected apps.")
        return

    st.divider()

    # ---- Radar Chart ----
    st.subheader("Performance Radar")
    fig = radar_chart(selected_apps)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---- Side-by-Side Metrics ----
    st.subheader("Key Metrics Comparison")

    cols = st.columns(len(selected_apps))
    for i, app in enumerate(selected_apps):
        with cols[i]:
            if app.get("icon_url"):
                st.image(app["icon_url"], width=64)
            st.markdown(f"**{app['name']}**")
            st.caption(app.get("publisher_name", ""))
            st.metric("Revenue", fmt_money(app.get("revenue", 0)))
            st.metric("Downloads", fmt_number(app.get("downloads", 0)))
            st.metric("Rating", fmt_rating(app.get("rating", 0)))
            st.metric("Total Ratings", fmt_number(app.get("global_rating_count", 0)))
            st.metric("Price", f"${app['price']:.2f}" if app.get("price", 0) > 0 else "Free")
            st.metric("Has IAP", "Yes" if app.get("in_app_purchases") else "No")

    st.divider()

    # ---- Comparison Table ----
    st.subheader("Full Comparison Table")

    metrics = [
        ("Revenue", lambda a: fmt_money(a.get("revenue", 0))),
        ("Downloads", lambda a: fmt_number(a.get("downloads", 0))),
        ("Rating", lambda a: fmt_rating(a.get("rating", 0))),
        ("Total Ratings", lambda a: fmt_number(a.get("global_rating_count", 0))),
        ("Price", lambda a: f"${a['price']:.2f}" if a.get("price", 0) > 0 else "Free"),
        ("IAP", lambda a: "Yes" if a.get("in_app_purchases") else "No"),
        ("Content Rating", lambda a: a.get("content_rating", "N/A")),
        ("Version", lambda a: a.get("version", "N/A")),
        ("Release Date", lambda a: (a.get("release_date", "")[:10] or "N/A")),
        ("Last Updated", lambda a: (a.get("updated_date", "")[:10] or "N/A")),
        ("Categories", lambda a: ", ".join(a.get("category_names", [])[:3])),
    ]

    rows = []
    for metric_name, extractor in metrics:
        row = {"Metric": metric_name}
        for app in selected_apps:
            row[app["name"][:25]] = extractor(app)
        rows.append(row)

    st.dataframe(rows, use_container_width=True, hide_index=True)
