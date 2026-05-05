from dash import html
import dash_bootstrap_components as dbc


def sidebar():
    nav_items = [
        {"label": "Dashboard", "icon": "📊", "href": "/dashboard"},
        {"label": "Emissions", "icon": "🏭", "href": "/emissions"},
        {"label": "AI Recommendations", "icon": "🤖", "href": "/recommendations"},
        {"label": "Scoring", "icon": "🏆", "href": "/scoring"},
    ]

    links = [
        dbc.NavLink(
            [html.Span(item["icon"], className="nav-icon"), html.Span(item["label"])],
            href=item["href"],
            active="exact",
            className="sidebar-link",
        )
        for item in nav_items
    ]

    return html.Div(
        [
            html.Div(
                [
                    html.Div("🌱", className="logo-icon"),
                    html.H4("CarbonAI", className="logo-text"),
                ],
                className="sidebar-logo",
            ),
            html.Hr(className="sidebar-divider"),
            dbc.Nav(links, vertical=True, pills=True, className="sidebar-nav"),
            html.Div(
                html.Small("v1.0.0 · AWS Serverless", className="text-muted"),
                className="sidebar-footer",
            ),
        ],
        className="sidebar",
    )
