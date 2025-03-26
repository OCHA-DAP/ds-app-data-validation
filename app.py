import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from callbacks.callbacks import register_callbacks
from constants import ISO3S, STAGE
from layouts.body import plots, sidebar_controls
from layouts.devbar import devbar
from layouts.navbar import navbar

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

register_callbacks(app)

layout = [
    navbar(title="Data Validation"),
    html.Div(
        [sidebar_controls(ISO3S, []), plots()],
        style={"display": "flex", "flexDirection": "row"},
    ),
    dcc.Store(id="raster-stats-data"),
]

if STAGE == "dev":
    layout.insert(0, devbar())

app.layout = html.Div(layout)

if __name__ == "__main__":
    app.run(debug=True)
