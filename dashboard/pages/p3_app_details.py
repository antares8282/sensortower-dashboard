"""App Details page — drill-down view for individual apps."""
import streamlit as st
from datetime import datetime
from components.data_loader import load_app_details
from components.formatters import fmt_money, fmt_number, fmt_rating


def render():
    st.title("App Details")

    app_id = st.session_state.get("selected_app_id")

    # Fallback to last viewed app if no selection
    if not app_id and "last_viewed_app_id" in st.session_state:
        app_id = st.session_state.last_viewed_app_id

    if not app_id:
        st.info("Select an app from Rankings or Opportunities to view details.")
        return

    # Store as last viewed
    st.session_state.last_viewed_app_id = app_id

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
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Est. Revenue", fmt_money(app.get("revenue", 0)))
    m2.metric("Est. Downloads", fmt_number(app.get("downloads", 0)))
    m3.metric("Price", f"${app['price']:.2f}" if app.get("price", 0) > 0 else "Free")
    m4.metric("Has IAP", "Yes" if app.get("in_app_purchases") else "No")
    m5.metric("App Age", f"{app_age} yrs" if app_age is not None else "N/A")

    st.divider()

    # ---- Rating & Reviews Section ----
    st.subheader("Ratings & Reviews")
    r1, r2, r3 = st.columns([2, 2, 3])

    with r1:
        rating = app.get("rating", 0)
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem; background: #1A1D23; border-radius: 12px;">
                <div style="font-size: 3.5rem; font-weight: 700; color: #FFD700; margin-bottom: 0.5rem;">
                    {fmt_rating(rating)}
                </div>
                <div style="font-size: 1.2rem; color: #888;">
                    {'⭐' * int(round(rating))}
                </div>
                <div style="margin-top: 0.5rem; color: #888; font-size: 0.9rem;">
                    Average Rating
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with r2:
        global_count = app.get("global_rating_count", 0)
        us_count = app.get("rating_count", 0)
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem; background: #1A1D23; border-radius: 12px;">
                <div style="font-size: 2rem; font-weight: 700; color: #4CAF50; margin-bottom: 0.5rem;">
                    {fmt_number(global_count)}
                </div>
                <div style="color: #888; font-size: 0.9rem; margin-bottom: 0.8rem;">
                    Global Ratings
                </div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #2196F3;">
                    {fmt_number(us_count)}
                </div>
                <div style="color: #888; font-size: 0.9rem;">
                    US Ratings
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with r3:
        st.markdown(
            """
            <div style="padding: 1.5rem; background: #1A1D23; border-radius: 12px;">
                <div style="color: #888; font-size: 0.9rem; margin-bottom: 1rem;">
                    <strong>📊 Rating Distribution</strong>
                </div>
                <div style="color: #666; font-style: italic; padding: 1.5rem; text-align: center;">
                    Rating breakdown not available<br/>
                    <span style="font-size: 0.8rem;">(Requires SensorTower Premium tier)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

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
