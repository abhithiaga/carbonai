import requests
import json
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from src.components.charts import category_bar_chart

API_BASE = "http://localhost:8000/api"
DEFAULT_ORG = "demo-org"

SCOPE_OPTIONS = [
    {"label": "Scope 1 – Direct", "value": "scope1"},
    {"label": "Scope 2 – Purchased Energy", "value": "scope2"},
    {"label": "Scope 3 – Value Chain", "value": "scope3"},
]

CATEGORY_OPTIONS = [
    {"label": cat.replace("_", " ").title(), "value": cat}
    for cat in ["energy", "transport", "waste", "supply_chain", "manufacturing", "agriculture", "other"]
]


def layout():
    return html.Div([
        html.H2("🏭 Emissions Data", className="page-title"),
        html.P("Log and review emission entries across all scopes", className="page-subtitle"),

        # ── Ingest form ──────────────────────────────────────────────
        dbc.Card(dbc.CardBody([
            html.H5("Add Emission Entry"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(id="entry-scope", options=SCOPE_OPTIONS, placeholder="Scope"), md=3),
                dbc.Col(dcc.Dropdown(id="entry-category", options=CATEGORY_OPTIONS, placeholder="Category"), md=3),
                dbc.Col(dbc.Input(id="entry-source", placeholder="Source (e.g. Gas Boiler)"), md=3),
                dbc.Col(dbc.Input(id="entry-amount", type="number", placeholder="kg CO2e", min=0), md=2),
                dbc.Col(dbc.Button("Add", id="entry-submit", color="success"), md=1),
            ], className="g-2"),
            html.Div(id="entry-feedback", className="mt-2"),
        ]), className="mb-4"),

        # ── Category bar chart ───────────────────────────────────────
        dcc.Graph(id="category-chart"),

        # ── Entries table ────────────────────────────────────────────
        html.H5("Emission Entries", className="mt-4 mb-2"),
        dash_table.DataTable(
            id="entries-table",
            columns=[
                {"name": "ID", "id": "id"},
                {"name": "Scope", "id": "scope"},
                {"name": "Category", "id": "category"},
                {"name": "Source", "id": "source"},
                {"name": "kg CO2e", "id": "amount_kg_co2e"},
                {"name": "Timestamp", "id": "timestamp"},
            ],
            data=[],
            style_table={"overflowX": "auto"},
            style_cell={"backgroundColor": "#242740", "color": "#e2e8f0", "border": "1px solid #2e3150"},
            style_header={"backgroundColor": "#1a1d2e", "fontWeight": "bold"},
            page_size=15,
        ),

        dcc.Interval(id="emissions-interval", interval=10_000, n_intervals=0),
    ], className="page-wrapper")


@callback(
    Output("entry-feedback", "children"),
    Input("entry-submit", "n_clicks"),
    State("entry-scope", "value"),
    State("entry-category", "value"),
    State("entry-source", "value"),
    State("entry-amount", "value"),
    prevent_initial_call=True,
)
def submit_entry(n, scope, category, source, amount):
    if not all([scope, category, source, amount]):
        return dbc.Alert("All fields required.", color="warning", duration=3000)
    try:
        payload = {
            "org_id": DEFAULT_ORG,
            "entries": [{"org_id": DEFAULT_ORG, "scope": scope, "category": category,
                         "source": source, "amount_kg_co2e": float(amount)}],
        }
        resp = requests.post(f"{API_BASE}/emissions/ingest", json=payload, timeout=5)
        data = resp.json()
        return dbc.Alert(f"✅ Added {data.get('inserted', 1)} entry.", color="success", duration=3000)
    except Exception as e:
        return dbc.Alert(f"Error: {e}", color="danger", duration=4000)


@callback(
    Output("category-chart", "figure"),
    Output("entries-table", "data"),
    Input("emissions-interval", "n_intervals"),
    Input("entry-submit", "n_clicks"),
)
def refresh_data(n, _):
    try:
        summary = requests.get(f"{API_BASE}/emissions/summary/{DEFAULT_ORG}", timeout=5).json()
        entries = requests.get(f"{API_BASE}/emissions/entries/{DEFAULT_ORG}?limit=100", timeout=5).json()
        by_cat = summary.get("by_category", {})
    except Exception:
        by_cat = {"energy": 52000, "transport": 38000, "waste": 15000, "supply_chain": 37500}
        entries = []

    fig = category_bar_chart(by_cat)
    table_data = [
        {**e, "timestamp": str(e.get("timestamp", ""))[:19]}
        for e in (entries if isinstance(entries, list) else [])
    ]
    return fig, table_data
