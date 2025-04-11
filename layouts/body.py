import dash_bootstrap_components as dbc
from dash import dcc, html

from src.utils import plot_utils

chart_style = {
    "marginRight": "15px",
    "marginBottom": "15px",
    "backgroundColor": "white",
    "border": "1px solid #eeeeee",
    "borderRadius": "5px",
}
dataset_options = {"seas5": "SEAS5", "floodscan": "Floodscan"}
stat_options = ["mean", "median", "min", "max", "count", "sum", "std"]


def sidebar_controls(iso3_options, date_options):
    return html.Div(
        [
            html.Div(
                [
                    dcc.Markdown(
                        """
                    This application is for basic validation and sanity checking of outputs from the
                    [COG](https://github.com/OCHA-DAP/ds-raster-pipelines) and [Raster Stat](https://github.com/OCHA-DAP/ds-raster-stats)
                    pipelines. Use the dropdowns below to explore available data. Please document any issues identified in the
                    appropriate GitHub repository.
                    """,
                        style={"marginBottom": "7px"},
                    )
                ]
            ),
            html.Hr(),
            html.Div(
                [
                    html.P("Select dataset:"),
                    dbc.Select(
                        id="dataset-dropdown",
                        options=dataset_options,
                        value=list(dataset_options.keys())[0],
                        className="mb-3",
                    ),
                ]
            ),
            html.Div(
                [
                    html.P("Select Issue Date:"),
                    dbc.Select(
                        id="issue-date-dropdown",
                        options=date_options,
                        className="mb-3",
                    ),
                ]
            ),
            # ISO3 Dropdown
            html.Div(
                [
                    html.P("Select ISO3 Code:"),
                    dbc.Select(
                        id="iso3-dropdown",
                        options=iso3_options,
                        className="mb-3",
                    ),
                ]
            ),
            # Admin Level Dropdown
            html.Div(
                [
                    html.P("Select Admin Level:"),
                    dbc.Select(
                        id="adm-level-dropdown",
                        options=[],
                        className="mb-3",
                    ),
                ]
            ),
            # PCODE Dropdown
            html.Div(
                [
                    html.P("Select Admin Unit:"),
                    dbc.Select(
                        id="pcode-dropdown",
                        options=[],
                        className="mb-3",
                    ),
                ]
            ),
            html.Div(
                [
                    html.P("Select stat:"),
                    dbc.Select(
                        id="stat-dropdown",
                        options=stat_options,
                        value=stat_options[0],
                        className="mb-3",
                    ),
                ]
            ),
            html.P("Raster display:"),
            dbc.RadioItems(
                id="raster-display",
                options=[
                    {"label": "Original", "value": "original"},
                    {"label": "Upsampled", "value": "upsampled"},
                ],
                value="original",
                inline=True,
                className="mb-3",
            ),
            html.Div(
                id="band-select-div",
                style={"display": "none"},
                children=[
                    html.P("Band:"),
                    dbc.RadioItems(
                        id="band-select",
                        options=["SFED", "MFED"],
                        value="SFED",
                        inline=True,
                        className="mb-3",
                    ),
                ],
            ),
        ],
        style={
            "width": "25%",
            "padding": "20px",
            "backgroundColor": "#ffffff",
            "height": "calc(100vh - 60px)",
            "overflowY": "auto",
        },
    )


def plots():
    return html.Div(
        [
            html.Div(
                [
                    dcc.Loading(
                        dcc.Graph(
                            id="chart-leadtime-series",
                            figure=plot_utils.blank_plot(),
                        ),
                        custom_spinner=dbc.Spinner(color="secondary"),
                    )
                ],
                style=chart_style,
            ),
            html.Div(
                [
                    dcc.Loading(
                        dcc.Graph(
                            id="chart-cog", figure=plot_utils.blank_plot()
                        ),
                        custom_spinner=dbc.Spinner(color="secondary"),
                    )
                ],
                style=chart_style,
            ),
        ],
        style={
            "width": "75%",
            "padding": "20px",
            "backgroundColor": "#ffffff",
            "height": "calc(100vh - 60px)",
            "overflowY": "auto",
        },
    )
