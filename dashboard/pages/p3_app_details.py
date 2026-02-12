"""App Details page — drill-down view for individual apps."""
import streamlit as st
from datetime import datetime
from components.data_loader import load_app_details
from components.formatters import fmt_money, fmt_number, fmt_rating


def render():
    st.title("App Details")

    app_id = st.session_state.get("selected_app_id")
    if not app_id:
        st.info("Select an app from the rankings table to view details.")
        return

    app_details = load_app_details()
    app = app_details.get(str(app_id), {})

    if not app:
        st.warning("App details not found.")
        return

    # ---- App Header ----
    col1, col2 = st.columns([1, 4])
    with col1:
        if app.get("icon_url"):
            st.image(app["icon_url"], width=120)
    with col2:
        st.markdown(f"### {app['name']}")
        st.caption(f"by **{app['publisher_name']}**")
        if app.get("subtitle"):
            st.markdown(f"*{app['subtitle']}*")
        cats = ", ".join(app.get("category_names", []))
        if cats:
            st.caption(f"Categories: {cats}")

    st.divider()

    # ---- Compute App Age ----
    app_age = None
    release_str = app.get("release_date", "")
    if release_str:
        try:
            release_dt = datetime.fromisoformat(release_str.replace("Z", "+00:00"))
            app_age = round((datetime.now(release_dt.tzinfo) - release_dt).days / 365.25, 1)
        except (ValueError, TypeError):
            pass

    # ---- Key Metrics ----
    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    m1.metric("Est. Revenue", fmt_money(app.get("revenue", 0)))
    m2.metric("Est. Downloads", fmt_number(app.get("downloads", 0)))
    m3.metric("Rating", fmt_rating(app.get("rating", 0)))
    m4.metric("Total Ratings", fmt_number(app.get("global_rating_count", 0)))
    m5.metric("Price", f"${app['price']:.2f}" if app.get("price", 0) > 0 else "Free")
    m6.metric("Has IAP", "Yes" if app.get("in_app_purchases") else "No")
    m7.metric("App Age", f"{app_age} yrs" if app_age is not None else "N/A")

    st.divider()

    # ---- Details Columns ----
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("App Information")

        info = {
            "Bundle ID": app.get("bundle_id", "N/A"),
            "Version": app.get("version", "N/A"),
            "Content Rating": app.get("content_rating", "N/A"),
            "Release Date": (app.get("release_date", "")[:10] or "N/A"),
            "Last Updated": (app.get("updated_date", "")[:10] or "N/A"),
            "Platform": app.get("os", "ios").upper(),
        }

        for k, v in info.items():
            st.markdown(f"**{k}:** {v}")

        # Languages
        langs = app.get("supported_languages", [])
        if langs:
            st.markdown(f"**Languages:** {', '.join(langs[:10])}" + (" + more" if len(langs) > 10 else ""))

        # Top countries
        countries = app.get("top_countries", [])
        if countries:
            st.markdown(f"**Top Countries:** {', '.join(countries[:10])}")

    with col_b:
        st.subheader("Description")
        desc = app.get("description", "No description available.")
        if len(desc) > 300:
            with st.expander("Show full description"):
                st.write(desc)
        else:
            st.write(desc)

    # ---- Screenshots ----
    screenshots = app.get("screenshot_urls", [])
    if screenshots:
        st.divider()
        st.subheader("Screenshots")
        cols = st.columns(min(len(screenshots), 5))
        for i, url in enumerate(screenshots[:5]):
            with cols[i]:
                st.image(url, use_container_width=True)

    # ---- App Store Link ----
    if app.get("url"):
        st.divider()
        st.link_button("View on App Store", app["url"])
