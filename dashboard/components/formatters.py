"""Number and date formatting helpers for the dashboard."""


def fmt_money(val):
    """Format integer to human-readable money: 238000000 → '$238M'"""
    if val is None or val == 0:
        return "$0"
    if val >= 1_000_000_000:
        return f"${val / 1_000_000_000:.1f}B"
    if val >= 1_000_000:
        return f"${val / 1_000_000:.0f}M"
    if val >= 1_000:
        return f"${val / 1_000:.0f}K"
    return f"${val:,.0f}"


def fmt_number(val):
    """Format integer to human-readable: 26000000 → '26M'"""
    if val is None or val == 0:
        return "0"
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.1f}B"
    if val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M"
    if val >= 1_000:
        return f"{val / 1_000:.0f}K"
    return f"{val:,}"


def fmt_rating(val):
    """Format rating: 4.53077 → '4.5'"""
    if val is None or val == 0:
        return "N/A"
    return f"{val:.1f}"


def fmt_delta(current, previous):
    """Format a delta value for st.metric: returns (formatted, delta_str)."""
    if previous is None or previous == 0:
        return fmt_money(current), None
    delta = current - previous
    pct = (delta / previous) * 100
    return fmt_money(current), f"{pct:+.1f}%"


CHART_TYPE_LABELS = {
    "topfreeapplications": "Top Free",
    "topgrossingapplications": "Top Grossing",
    "toppaidapplications": "Top Paid",
}
