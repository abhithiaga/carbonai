import requests
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from src.components.charts import emission_trend_chart, scope_breakdown_donut
from src.components.cards import stat_card

API_BASE = "http://localhost:8000/api"
DEFAULT_ORG = "demo-org"


def layout():
    return html.Div([
        html.H2("📊 Dashboard", className="page-title"),
        html.P("Real-time carbon footprint overview", className="page-subtitle"),
        html.Div(id="dashboard-stats"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="trend-chart"), md=8),
            dbc.Col(dcc.Graph(id="scope-donut"), md=4),
        ], className="mt-3"),
        dcc.Interval(id="dashboard-interval", interval=30_000, n_intervals=0),
    ], className="page-wrapper")


@callback(
    Output("dashboard-stats", "children"),
    Output("trend-chart", "figure"),
    Output("scope-donut", "figure"),
    Input("dashboard-interval", "n_intervals"),
)
def update_dashboard(n):
    try:
        summary = requests.get(f"{API_BASE}/emissions/summary/{DEFAULT_ORG}", timeout=5).json()
        trend_resp = requests.get(f"{API_BASE}/emissions/trend/{DEFAULT_ORG}?months=12", timeout=5).json()
        trend_data = trend_resp.get("data", [])
    except Exception:
        # Fallback mock data for local dev without backend
        summary = {
            "total_kg_co2e": 142500,
            "by_scope": {"scope1": 45000, "scope2": 52000, "scope3": 45500},
            "by_category": {"energy": 52000, "transport": 38000, "waste": 15000, "supply_chain": 37500},
            "trend_pct": -8.4,
        }
        trend_data = [
            {"month": f"2024-{i:02d}", "total_kg_co2e": 14000 - i * 200}
            for i in range(1, 13)
        ]

    total = summary.get("total_kg_co2e", 0)
    trend_pct = summary.get("trend_pct")
    trend_str = f"{'↓' if trend_pct and trend_pct < 0 else '↑'} {abs(trend_pct):.1f}% vs prior period" if trend_pct else ""

    stats_row = dbc.Row([
        dbc.Col(stat_card("Total Emissions", f"{total/1000:,.1f} t CO2e", trend_str, icon="🌍"), md=3),
        dbc.Col(stat_card("Scope 1", f"{summary['by_scope'].get('scope1',0)/1000:,.1f} t", "Direct", color="#00c896", icon="🔥"), md=3),
        dbc.Col(stat_card("Scope 2", f"{summary['by_scope'].get('scope2',0)/1000:,.1f} t", "Purchased Energy", color="#00a3e0", icon="⚡"), md=3),
        dbc.Col(stat_card("Scope 3", f"{summary['by_scope'].get('scope3',0)/1000:,.1f} t", "Value Chain", color="#f97316", icon="🔗"), md=3),
    ])

    trend_fig = emission_trend_chart(trend_data)
    donut_fig = scope_breakdown_donut(summary.get("by_scope", {}))

    return stats_row, trend_fig, donut_fig
