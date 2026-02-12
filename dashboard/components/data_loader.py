"""Load dashboard data with Streamlit caching."""
import json
from pathlib import Path
import streamlit as st

DATA_DIR = Path(__file__).parent.parent.parent / "dashboard_data"


@st.cache_data(ttl=300)
def load_rankings():
    with open(DATA_DIR / "current" / "rankings.json") as f:
        return json.load(f)


@st.cache_data(ttl=300)
def load_app_details():
    with open(DATA_DIR / "current" / "app_details.json") as f:
        return json.load(f)


@st.cache_data(ttl=300)
def load_category_summary():
    with open(DATA_DIR / "current" / "category_summary.json") as f:
        return json.load(f)


@st.cache_data(ttl=300)
def load_publisher_summary():
    with open(DATA_DIR / "current" / "publisher_summary.json") as f:
        return json.load(f)


@st.cache_data(ttl=300)
def load_trends():
    path = DATA_DIR / "historical" / "trends.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"dates": [], "categories": {}}


@st.cache_data(ttl=300)
def load_metadata():
    path = DATA_DIR / "metadata.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def get_app_by_id(app_id):
    """Look up a single app from the details cache."""
    details = load_app_details()
    return details.get(str(app_id), {})


def get_all_apps_list():
    """Return a list of (app_id, name) tuples sorted by name."""
    details = load_app_details()
    apps = [(aid, a["name"]) for aid, a in details.items()]
    apps.sort(key=lambda x: x[1])
    return apps


@st.cache_data(ttl=300)
def load_all_apps_table():
    with open(DATA_DIR / "current" / "all_apps_table.json") as f:
        return json.load(f)
