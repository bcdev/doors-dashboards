from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

SELECT_MAP_STYLE_DRP = "mapstyle-drp"

popup = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Select Map Types"),
                dbc.ModalBody(
                    [
                        dbc.Label("Choose an option:"),
                        dcc.Dropdown(
                            id=SELECT_MAP_STYLE_DRP,
                            options=[
                                {
                                    "label": "Open Street Map",
                                    "value": "open-street-map",
                                },
                                {
                                    "label": "Carto Darkmatter",
                                    "value": "carto-darkmatter",
                                },
                                {"label": "White background", "value": "white-bg"},
                                {"label": "Carto Positron", "value": "carto-positron"},
                            ],
                            value="carto-positron",
                        ),
                    ]
                ),
            ],
            id="modal",
        ),
    ]
)
