"""
PowerStack Labs — Market Intelligence Dashboard
Entry point for the Streamlit app.
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from components.auth import check_password

st.set_page_config(
    page_title="PowerStack Labs | Market Intel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Auth gate
if not check_password():
    st.stop()

# --- Authenticated content ---

# Sidebar branding
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
        <h2 style="margin: 0;">📊 PowerStack</h2>
        <p style="color: #888; margin: 0; font-size: 0.85rem;">Market Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Navigation
page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Overview",
        "📱 Rankings",
        "🔍 App Details",
        "📈 Trends",
        "🏢 Publishers",
        "⚖️ Compare",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()

# Load metadata for sidebar
from components.data_loader import load_metadata
meta = load_metadata()
if meta:
    last_refresh = meta.get("last_refresh", "Unknown")[:16].replace("T", " ")
    st.sidebar.caption(f"Last updated: {last_refresh}")
    st.sidebar.caption(f"Apps tracked: {meta.get('total_apps', '?')}")
    st.sidebar.caption(f"Platform: {meta.get('platform', 'iOS')} • {meta.get('country', 'US')}")

# Logout
st.sidebar.divider()
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

# Route to pages
if page == "🏠 Overview":
    from pages.p1_overview import render
    render()
elif page == "📱 Rankings":
    from pages.p2_rankings import render
    render()
elif page == "🔍 App Details":
    from pages.p3_app_details import render
    render()
elif page == "📈 Trends":
    from pages.p4_trends import render
    render()
elif page == "🏢 Publishers":
    from pages.p5_publishers import render
    render()
elif page == "⚖️ Compare":
    from pages.p6_compare import render
    render()
