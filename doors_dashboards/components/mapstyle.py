from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc

SELECT_MAPSTYLE_DRP = 'mapstyle-drp'

popup = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Select Map Types"),
                dbc.ModalBody(
                    [
                        dbc.Label("Choose an option:"),
                        dcc.Dropdown(
                            id=SELECT_MAPSTYLE_DRP,
                            options=[
                                {"label": "Open Street Map", "value":
                                    "open-street-map"},
                                {"label": "Carto Darkmatter", "value":
                                    "carto-darkmatter"},
                                {"label": "Basic", "value":
                                    "basic"},
                                {"label": "Streets", "value":
                                    "streets"},
                            ],
                            value=None,
                        ),
                    ]
                ),
            ],
            id="modal",
        ),
    ]
)