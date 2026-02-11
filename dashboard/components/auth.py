"""Authentication wrapper for the dashboard.

For local development, set environment variables:
  DASHBOARD_USERNAME=admin
  DASHBOARD_PASSWORD=yourpassword

For Streamlit Cloud, configure in the Secrets UI.
"""
import os
import hashlib
import streamlit as st


def check_password():
    """Returns True if the user has entered the correct password."""

    def _hash(pw):
        return hashlib.sha256(pw.encode()).hexdigest()

    # Get credentials from secrets or env vars
    try:
        correct_user = st.secrets["auth"]["username"]
        correct_hash = st.secrets["auth"]["password_hash"]
    except (KeyError, FileNotFoundError):
        correct_user = os.getenv("DASHBOARD_USERNAME", "admin")
        correct_pw = os.getenv("DASHBOARD_PASSWORD", "sensortower2025")
        correct_hash = _hash(correct_pw)

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Login form
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1>📊 PowerStack Labs</h1>
            <h3 style="color: #888;">Market Intelligence Dashboard</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in", use_container_width=True)

            if submitted:
                if username == correct_user and _hash(password) == correct_hash:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    return False
