import dash_bootstrap_components as dbc
from dash import html


def navbar(title):
    return html.Div(
        [
            dbc.NavbarBrand(
                title,
                style={"margin": "0"},
                className=["ms-2", "header", "bold"],
            ),
        ],
        style={
            "backgroundColor": "#eeeeee",
            "height": "60px",
            "padding": "10px",
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
        },
    )
