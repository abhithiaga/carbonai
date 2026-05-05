import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from src.components.sidebar import sidebar
from src.pages import dashboard, emissions, recommendations, scoring

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "CarbonAI – Sustainability Platform"
server = app.server  # for AWS Lambda / gunicorn

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="org-store", storage_type="session"),   # stores org_id + token
        dbc.Row(
            [
                dbc.Col(sidebar(), width=2, className="sidebar-col"),
                dbc.Col(
                    html.Div(id="page-content", className="page-content"),
                    width=10,
                ),
            ],
            className="g-0 main-row",
        ),
    ],
    className="app-wrapper",
)

# ─── Page routing callback ────────────────────────────────────────────────────
from dash.dependencies import Input, Output

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname == "/" or pathname == "/dashboard":
        return dashboard.layout()
    elif pathname == "/emissions":
        return emissions.layout()
    elif pathname == "/recommendations":
        return recommendations.layout()
    elif pathname == "/scoring":
        return scoring.layout()
    return html.Div([html.H3("404 – Page not found")], className="p-4")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
