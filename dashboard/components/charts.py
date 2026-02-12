"""Reusable Plotly chart builders for the dashboard."""
import plotly.express as px
import plotly.graph_objects as go
from .formatters import fmt_money, fmt_number


COLORS = {
    "Utilities": "#FF6B6B",
    "Business": "#4ECDC4",
    "Photo & Video": "#45B7D1",
    "Productivity": "#96CEB4",
    "Lifestyle": "#FFEAA7",
    "Health & Fitness": "#DDA0DD",
}

CHART_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"


def _base_layout(fig, title=None):
    """Apply consistent dark theme to a Plotly figure."""
    fig.update_layout(
        title=title,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color="#FAFAFA", size=13),
        margin=dict(l=20, r=20, t=40 if title else 20, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FAFAFA"),
        ),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)")
    return fig


def revenue_by_category_bar(cat_summary):
    """Horizontal bar chart of revenue by category."""
    cats = list(cat_summary.keys())
    revenues = [cat_summary[c]["grossing_revenue"] for c in cats]
    colors = [COLORS.get(c, "#888") for c in cats]

    fig = go.Figure(go.Bar(
        x=revenues,
        y=cats,
        orientation="h",
        marker_color=colors,
        text=[fmt_money(r) for r in revenues],
        textposition="auto",
        textfont=dict(color="white"),
    ))
    _base_layout(fig)
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=300,
        xaxis_title="Estimated Monthly Revenue",
    )
    return fig


def downloads_by_category_bar(cat_summary):
    """Horizontal bar chart of downloads by category."""
    cats = list(cat_summary.keys())
    downloads = [cat_summary[c]["grossing_downloads"] for c in cats]
    colors = [COLORS.get(c, "#888") for c in cats]

    fig = go.Figure(go.Bar(
        x=downloads,
        y=cats,
        orientation="h",
        marker_color=colors,
        text=[fmt_number(d) for d in downloads],
        textposition="auto",
        textfont=dict(color="white"),
    ))
    _base_layout(fig)
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=300,
        xaxis_title="Estimated Monthly Downloads",
    )
    return fig


def top_apps_revenue_bar(apps, n=10):
    """Horizontal bar chart of top N apps by revenue."""
    sorted_apps = sorted(apps, key=lambda x: x.get("revenue", 0), reverse=True)[:n]
    sorted_apps.reverse()  # Plotly renders bottom-up

    names = [a["name"][:25] for a in sorted_apps]
    revenues = [a.get("revenue", 0) for a in sorted_apps]

    fig = go.Figure(go.Bar(
        x=revenues,
        y=names,
        orientation="h",
        marker_color="#FF6B6B",
        text=[fmt_money(r) for r in revenues],
        textposition="auto",
        textfont=dict(color="white"),
    ))
    _base_layout(fig)
    fig.update_layout(height=max(300, n * 35))
    return fig


def publisher_treemap(pub_summary, n=20):
    """Treemap of top publishers by revenue."""
    top = sorted(pub_summary, key=lambda x: x["total_revenue"], reverse=True)[:n]
    top = [p for p in top if p["total_revenue"] > 0]

    if not top:
        return go.Figure()

    fig = px.treemap(
        names=[p["publisher_name"][:20] for p in top],
        parents=["" for _ in top],
        values=[p["total_revenue"] for p in top],
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    _base_layout(fig)
    fig.update_layout(height=400)
    fig.update_traces(
        textinfo="label+value",
        texttemplate="%{label}<br>%{value:$,.0s}",
    )
    return fig


def trends_line_chart(trends_data, metric="grossing_revenue"):
    """Line chart of a metric over time by category."""
    if not trends_data.get("dates"):
        return None

    fig = go.Figure()
    for cat_name, cat_data in trends_data.get("categories", {}).items():
        values = cat_data.get(metric, [])
        if values:
            fig.add_trace(go.Scatter(
                x=trends_data["dates"],
                y=values,
                name=cat_name,
                mode="lines+markers",
                line=dict(color=COLORS.get(cat_name, "#888"), width=2),
            ))

    _base_layout(fig)
    fig.update_layout(height=400)
    return fig


def radar_chart(apps_data):
    """Radar chart comparing multiple apps across normalized metrics."""
    if not apps_data:
        return go.Figure()

    metrics = ["rating", "revenue", "downloads", "global_rating_count"]
    metric_labels = ["Rating", "Revenue", "Downloads", "Total Ratings"]

    # Normalize each metric to 0-1
    max_vals = {}
    for m in metrics:
        vals = [a.get(m, 0) for a in apps_data]
        max_vals[m] = max(vals) if max(vals) > 0 else 1

    fig = go.Figure()
    for app in apps_data:
        values = [app.get(m, 0) / max_vals[m] for m in metrics]
        values.append(values[0])  # Close the shape
        labels = metric_labels + [metric_labels[0]]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill="toself",
            name=app.get("name", "Unknown")[:20],
            opacity=0.6,
        ))

    _base_layout(fig)
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        ),
        height=450,
    )
    return fig
