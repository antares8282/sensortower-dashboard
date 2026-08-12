"""Authentication wrapper for the dashboard.

Credentials are hardcoded (hash-compared) below rather than read from env
vars or Streamlit secrets. Render's DASHBOARD_USERNAME/DASHBOARD_PASSWORD
env vars were previously wired up but drifted out of sync with what's in
this file, which silently locked out the real credentials. This file is
now the single source of truth — change CORRECT_USER/CORRECT_HASH here to
rotate the password.
"""
import hashlib
import streamlit as st

CORRECT_USER = "gokhan"
# sha256("PowerStack-2026!")
CORRECT_HASH = "642f77dee5ceacd1fdaff6d417cd6e26330a8315ba7a14dcf0163422bf6ae186"


def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def check_password():
    """Returns True if the user has entered the correct password."""

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
                if username == CORRECT_USER and _hash(password) == CORRECT_HASH:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    return False
