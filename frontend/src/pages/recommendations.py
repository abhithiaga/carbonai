import requests
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from src.components.cards import recommendation_card

API_BASE = "http://localhost:8000/api"
DEFAULT_ORG = "demo-org"

FOCUS_OPTIONS = [
    {"label": "All Areas", "value": ""},
    {"label": "Energy", "value": "energy"},
    {"label": "Transport", "value": "transport"},
    {"label": "Waste", "value": "waste"},
    {"label": "Supply Chain", "value": "supply_chain"},
]


def layout():
    return html.Div([
        html.H2("🤖 AI Recommendations", className="page-title"),
        html.P("LLM-powered, data-driven carbon reduction strategies", className="page-subtitle"),

        dbc.Card(dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Focus Area"),
                    dcc.Dropdown(id="rec-focus", options=FOCUS_OPTIONS, value="", clearable=False),
                ], md=4),
                dbc.Col([
                    html.Label("Target Reduction (%)"),
                    dbc.Input(id="rec-target", type="number", value=20, min=1, max=100),
                ], md=3),
                dbc.Col([
                    html.Label("Additional Context (optional)"),
                    dbc.Input(id="rec-context", placeholder="e.g. we operate in cold climate"),
                ], md=4),
                dbc.Col(
                    dbc.Button("Generate", id="rec-submit", color="success", className="w-100 mt-4"),
                    md=1
                ),
            ], className="g-2"),
        ]), className="mb-4"),

        dbc.Spinner(
            html.Div(id="rec-output"),
            color="success",
            spinner_style={"width": "3rem", "height": "3rem"},
        ),
    ], className="page-wrapper")


@callback(
    Output("rec-output", "children"),
    Input("rec-submit", "n_clicks"),
    State("rec-focus", "value"),
    State("rec-target", "value"),
    State("rec-context", "value"),
    prevent_initial_call=True,
)
def generate_recommendations(n, focus, target, context):
    try:
        payload = {
            "org_id": DEFAULT_ORG,
            "focus_area": focus or None,
            "target_reduction_pct": float(target or 20),
            "context": context or None,
        }
        resp = requests.post(f"{API_BASE}/recommendations/generate", json=payload, timeout=60)
        data = resp.json()
    except Exception as e:
        # Fallback mock when backend is offline
        data = {
            "recommendations": [
                {
                    "title": "Switch to Renewable Energy",
                    "description": "Transition electricity procurement to 100% renewable sources via PPAs or green tariffs.",
                    "category": "energy",
                    "estimated_reduction_kg_co2e": 52000,
                    "implementation_cost": "medium",
                    "timeframe": "short_term",
                    "priority": 1,
                },
                {
                    "title": "Fleet Electrification",
                    "description": "Replace company vehicles with EVs, reducing transport Scope 1 emissions.",
                    "category": "transport",
                    "estimated_reduction_kg_co2e": 18000,
                    "implementation_cost": "high",
                    "timeframe": "long_term",
                    "priority": 2,
                },
                {
                    "title": "LED Lighting Retrofit",
                    "description": "Upgrade all facility lighting to LED, reducing electricity demand by ~40%.",
                    "category": "energy",
                    "estimated_reduction_kg_co2e": 8000,
                    "implementation_cost": "low",
                    "timeframe": "immediate",
                    "priority": 3,
                },
            ],
            "estimated_reduction_kg_co2e": 78000,
            "priority_actions": ["Renewable energy PPA", "EV fleet transition", "LED retrofit"],
        }

    recs = data.get("recommendations", [])
    total_est = data.get("estimated_reduction_kg_co2e", 0)
    priority_actions = data.get("priority_actions", [])

    return html.Div([
        dbc.Alert([
            html.Strong("🎯 Estimated Total Reduction: "),
            f"{total_est:,.0f} kg CO2e",
            html.Br(),
            html.Strong("Priority Actions: "),
            ", ".join(priority_actions),
        ], color="success", className="mb-3"),
        html.Div([recommendation_card(r, i + 1) for i, r in enumerate(recs)]),
    ])
