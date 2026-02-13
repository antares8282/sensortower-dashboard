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
USE_AUTH = False  # Set to True to re-enable authentication
if USE_AUTH and not check_password():
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

# Load metadata for sidebar
from components.data_loader import load_metadata
meta = load_metadata()
if meta:
    last_refresh = meta.get("last_refresh", "Unknown")[:16].replace("T", " ")
    st.sidebar.caption(f"Last updated: {last_refresh}")
    st.sidebar.caption(f"Apps tracked: {meta.get('total_apps', '?')}")
    st.sidebar.caption(f"Platform: {meta.get('platform', 'iOS')} • {meta.get('country', 'US')}")

    # API usage counter
    usage = meta.get("api_usage_monthly", 0)
    budget = 2500
    pct = usage / budget * 100
    if usage >= 2000:
        color = "#FF4B4B"
    elif usage >= 1500:
        color = "#FFA500"
    else:
        color = "#4CAF50"
    st.sidebar.markdown(
        f'<div style="background:{color}22; border:1px solid {color}; border-radius:8px; '
        f'padding:6px 12px; text-align:center; margin-top:8px;">'
        f'<span style="color:{color}; font-weight:600; font-size:0.85rem;">'
        f'🔑 API: {usage:,} / {budget:,} ({pct:.1f}%)</span></div>',
        unsafe_allow_html=True,
    )

st.sidebar.divider()

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "rankings"

# Sidebar navigation
st.sidebar.markdown("### Navigation")
if st.sidebar.button(
    "📊 Rankings",
    use_container_width=True,
    type="primary" if st.session_state.page == "rankings" else "secondary"
):
    st.session_state.page = "rankings"
    if "selected_app_id" in st.session_state:
        del st.session_state.selected_app_id
    st.rerun()

if st.sidebar.button(
    "💡 Opportunities",
    use_container_width=True,
    type="primary" if st.session_state.page == "opportunities" else "secondary"
):
    st.session_state.page = "opportunities"
    if "selected_app_id" in st.session_state:
        del st.session_state.selected_app_id
    st.rerun()

if st.sidebar.button(
    "🔍 App Details",
    use_container_width=True,
    type="primary" if st.session_state.page == "app_details" else "secondary"
):
    st.session_state.page = "app_details"
    st.rerun()

st.sidebar.divider()

# Auto-switch to app details on selection
if st.session_state.get("selected_app_id"):
    st.session_state.page = "app_details"

# Route to pages
if st.session_state.page == "app_details":
    from pages.p3_app_details import render
    render()
elif st.session_state.page == "opportunities":
    from pages.p2_opportunities import render
    render()
else:  # rankings
    from pages.p1_rankings import render
    render()

# Logout
st.sidebar.divider()
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()
