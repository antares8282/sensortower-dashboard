"""Authentication wrapper for the dashboard.

Credentials are hardcoded (hash-compared) below rather than read from env
vars or Streamlit secrets. Render's DASHBOARD_USERNAME/DASHBOARD_PASSWORD
env vars were previously wired up but drifted out of sync with what's in
this file, which silently locked out the real credentials. This file is
now the single source of truth — change CORRECT_USER/CORRECT_HASH here to
rotate the password.

A successful login also drops an encrypted "remember this browser" cookie
so the same machine/browser isn't asked again until it expires (~1 year).
This is per-browser, not per-machine — a different browser, or clearing
cookies, means logging in again.

get_cookie_manager() must be called exactly once per script run, from the
top of app.py (not cached at module import time) — Streamlit reruns the
whole entrypoint script on every interaction but does not re-execute an
already-imported module's body, so a module-level instance would freeze
on whichever browser happened to trigger the first import and get served
to every session after that.
"""
import hashlib
import streamlit as st

# streamlit_cookies_manager is unmaintained and still decorates a function with
# @st.cache, an API Streamlit has since removed entirely (not just deprecated).
# requirements.txt pins streamlit loosely (>=1.30.0), so a routine Render
# rebuild resolved a newer Streamlit and broke this import in production —
# AttributeError: module 'streamlit' has no attribute 'cache'. Shim it back in
# as an alias for its direct replacement before the import runs.
if not hasattr(st, "cache"):
    st.cache = st.cache_data

from streamlit_cookies_manager import EncryptedCookieManager  # noqa: E402

CORRECT_USER = "gokhan"
# sha256("PowerStack-2026!")
CORRECT_HASH = "642f77dee5ceacd1fdaff6d417cd6e26330a8315ba7a14dcf0163422bf6ae186"

# Encrypts the cookie payload client-side only — not a login secret itself.
_COOKIE_PASSWORD = "cVHeR-Dahe8dyN_ZSEp6_Q7raJuVClMxOgkRkA1KST4"


def get_cookie_manager():
    return EncryptedCookieManager(prefix="powerstack/", password=_COOKIE_PASSWORD)


def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def check_password(cookies):
    """Returns True if the session (or a remembered cookie) is authenticated."""

    if not cookies.ready():
        # Cookie component needs one rerun to sync from the browser.
        st.stop()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    if cookies.get("authenticated") == "true":
        st.session_state.authenticated = True
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
                    cookies["authenticated"] = "true"
                    cookies.save()
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    return False
