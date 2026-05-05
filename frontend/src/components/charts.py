import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict

COLORS = {
    "scope1": "#00c896",
    "scope2": "#00a3e0",
    "scope3": "#f97316",
    "bg": "#1a1d2e",
    "paper": "#242740",
    "grid": "#2e3150",
    "text": "#e2e8f0",
}

BASE_LAYOUT = dict(
    paper_bgcolor=COLORS["paper"],
    plot_bgcolor=COLORS["bg"],
    font=dict(color=COLORS["text"], family="Space Grotesk"),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
    yaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
)


def emission_trend_chart(trend_data: List[Dict]) -> go.Figure:
    """Line chart of monthly emissions."""
    months = [d["month"] for d in trend_data]
    totals = [d["total_kg_co2e"] for d in trend_data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=totals,
        mode="lines+markers",
        name="Total CO2e",
        line=dict(color=COLORS["scope1"], width=3),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(0,200,150,0.08)",
    ))
    fig.update_layout(**BASE_LAYOUT, title="Monthly Emissions Trend")
    return fig


def scope_breakdown_donut(by_scope: Dict) -> go.Figure:
    """Donut chart for scope breakdown."""
    labels = list(by_scope.keys())
    values = list(by_scope.values())
    colors = [COLORS.get(k, "#888") for k in labels]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo="label+percent",
        textfont=dict(color=COLORS["text"]),
    ))
    fig.update_layout(
        **{k: v for k, v in BASE_LAYOUT.items() if k not in ("xaxis", "yaxis")},
        title="Emissions by Scope",
        showlegend=True,
    )
    return fig


def category_bar_chart(by_category: Dict) -> go.Figure:
    """Horizontal bar chart for category breakdown."""
    cats = list(by_category.keys())
    vals = list(by_category.values())

    fig = go.Figure(go.Bar(
        x=vals, y=cats,
        orientation="h",
        marker=dict(
            color=vals,
            colorscale=[[0, COLORS["scope1"]], [1, COLORS["scope3"]]],
        ),
        text=[f"{v:,.0f}" for v in vals],
        textposition="auto",
    ))
    fig.update_layout(**BASE_LAYOUT, title="Emissions by Category (kg CO2e)")
    return fig


def score_gauge(score: float, grade: str) -> go.Figure:
    """Gauge chart for sustainability score."""
    color = "#00c896" if score >= 70 else "#f97316" if score >= 50 else "#ef4444"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": 50},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["text"]},
            "bar": {"color": color},
            "bgcolor": COLORS["bg"],
            "bordercolor": COLORS["grid"],
            "steps": [
                {"range": [0, 50], "color": "#2d1f1f"},
                {"range": [50, 75], "color": "#1f2d2a"},
                {"range": [75, 100], "color": "#1a2d25"},
            ],
        },
        title={"text": f"Sustainability Score — Grade {grade}", "font": {"color": COLORS["text"]}},
        number={"font": {"color": color, "size": 48}},
    ))
    fig.update_layout(
        paper_bgcolor=COLORS["paper"],
        font=dict(color=COLORS["text"], family="Space Grotesk"),
        margin=dict(l=30, r=30, t=60, b=20),
    )
    return fig
