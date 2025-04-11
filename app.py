import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from callbacks.callbacks import register_callbacks
from constants import STAGE
from layouts.body import plots, sidebar_controls
from layouts.devbar import devbar
from layouts.navbar import navbar

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
server = app.server
app.title = "DSCI Data Validation"

register_callbacks(app)

layout = [
    navbar(title="Data Validation"),
    html.Div(
        [sidebar_controls([], []), plots()],
        style={"display": "flex", "flexDirection": "row"},
    ),
    dcc.Store(id="raster-stats-data"),
    dcc.Store(id="iso3-data"),
    dcc.Interval(
        id="interval-component", interval=500, max_intervals=1
    ),  # Fires once, half second after page load
]

if STAGE == "dev":
    layout.insert(0, devbar())

app.layout = html.Div(layout)

if __name__ == "__main__":
    app.run(debug=True)
