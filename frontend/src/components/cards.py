from dash import html
import dash_bootstrap_components as dbc


def stat_card(title: str, value: str, subtitle: str = "", color: str = "#00c896", icon: str = ""):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Span(icon, className="stat-icon") if icon else None,
                html.P(title, className="stat-title"),
            ], className="stat-header"),
            html.H2(value, className="stat-value", style={"color": color}),
            html.Small(subtitle, className="text-muted") if subtitle else None,
        ]),
        className="stat-card",
    )


def recommendation_card(rec: dict, rank: int):
    cost_color = {"low": "#00c896", "medium": "#f97316", "high": "#ef4444"}.get(
        rec.get("implementation_cost", "medium"), "#888"
    )
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(html.H2(f"#{rank}", className="rec-rank"), width="auto"),
                dbc.Col([
                    html.H5(rec.get("title", ""), className="rec-title"),
                    html.P(rec.get("description", ""), className="rec-desc"),
                    dbc.Row([
                        dbc.Col(dbc.Badge(
                            rec.get("category", "").upper(),
                            color="secondary", className="me-1"
                        ), width="auto"),
                        dbc.Col(dbc.Badge(
                            f"Cost: {rec.get('implementation_cost','?')}",
                            style={"backgroundColor": cost_color}, className="me-1"
                        ), width="auto"),
                        dbc.Col(dbc.Badge(
                            rec.get("timeframe", "").replace("_", " ").title(),
                            color="info"
                        ), width="auto"),
                    ]),
                ]),
                dbc.Col([
                    html.Div([
                        html.Small("Est. Reduction", className="text-muted d-block"),
                        html.Strong(
                            f"{rec.get('estimated_reduction_kg_co2e', 0):,.0f} kg",
                            style={"color": "#00c896"}
                        ),
                    ])
                ], width=2, className="text-end"),
            ], align="center"),
        ]),
        className="rec-card mb-3",
    )
