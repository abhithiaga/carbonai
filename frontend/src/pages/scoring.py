import requests
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from src.components.charts import score_gauge

API_BASE = "http://localhost:8000/api"
DEFAULT_ORG = "demo-org"

INDUSTRY_OPTIONS = [
    {"label": ind.title(), "value": ind}
    for ind in ["technology", "manufacturing", "retail", "finance", "healthcare", "energy", "agriculture"]
]


def layout():
    return html.Div([
        html.H2("🏆 Sustainability Score", className="page-title"),
        html.P("AI-computed score vs industry benchmarks", className="page-subtitle"),

        dbc.Card(dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Industry Benchmark"),
                    dcc.Dropdown(id="score-industry", options=INDUSTRY_OPTIONS, value="technology"),
                ], md=4),
                dbc.Col(
                    dbc.Button("Calculate Score", id="score-submit", color="success", className="mt-4"),
                    md=2
                ),
            ], className="g-2"),
        ]), className="mb-4"),

        dbc.Spinner(html.Div(id="score-output"), color="success"),

        html.H5("🏅 Leaderboard", className="mt-4 mb-2"),
        html.Div(id="leaderboard-output"),
        dcc.Interval(id="score-interval", interval=60_000, n_intervals=0),
    ], className="page-wrapper")


@callback(
    Output("score-output", "children"),
    Input("score-submit", "n_clicks"),
    State("score-industry", "value"),
    prevent_initial_call=True,
)
def calculate_score(n, industry):
    try:
        resp = requests.post(
            f"{API_BASE}/scoring/score",
            json={"org_id": DEFAULT_ORG, "benchmark_industry": industry},
            timeout=10,
        )
        data = resp.json()
    except Exception:
        data = {
            "overall_score": 74.2,
            "grade": "B",
            "subscores": {"scope1": 82, "scope2": 68, "scope3": 72},
            "industry_percentile": 70.5,
            "improvement_areas": ["scope2"],
        }

    gauge_fig = score_gauge(data["overall_score"], data["grade"])
    subscores = data.get("subscores", {})

    return html.Div([
        dcc.Graph(figure=gauge_fig, style={"height": "320px"}),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Industry Percentile", className="stat-title"),
                html.H3(f"{data.get('industry_percentile', 0):.1f}%", style={"color": "#00c896"}),
            ])), md=4),
            *[
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.P(k.upper(), className="stat-title"),
                    html.H3(f"{v}/100", style={"color": "#00a3e0"}),
                ])), md=2)
                for k, v in subscores.items()
            ],
        ], className="mt-3"),
        html.Div([
            dbc.Alert(f"⚠️ Improvement needed in: {', '.join(data.get('improvement_areas', []))}", color="warning")
        ] if data.get("improvement_areas") else []),
    ])


@callback(
    Output("leaderboard-output", "children"),
    Input("score-interval", "n_intervals"),
)
def refresh_leaderboard(n):
    try:
        board = requests.get(f"{API_BASE}/scoring/leaderboard?limit=10", timeout=5).json()
    except Exception:
        board = [
            {"org_id": "acme-corp", "score": 88.4, "grade": "A"},
            {"org_id": "greentech-inc", "score": 76.1, "grade": "B"},
            {"org_id": "demo-org", "score": 74.2, "grade": "B"},
        ]

    rows = [
        html.Tr([
            html.Td(f"#{i+1}", style={"color": "#f97316"}),
            html.Td(entry.get("org_id", "")),
            html.Td(f"{entry.get('score', 0):.1f}", style={"color": "#00c896"}),
            html.Td(dbc.Badge(entry.get("grade", "?"), color="success")),
        ])
        for i, entry in enumerate(board)
    ]

    return dbc.Table(
        [html.Thead(html.Tr([html.Th("Rank"), html.Th("Organization"), html.Th("Score"), html.Th("Grade")])),
         html.Tbody(rows)],
        bordered=True, hover=True, dark=True, responsive=True,
    )
