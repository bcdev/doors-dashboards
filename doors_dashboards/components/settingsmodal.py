from dash import dcc
import dash_bootstrap_components as dbc

SELECT_MAP_STYLE_DRP = "mapstyle-drp"


def create_settings_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Settings")),
        dbc.ModalBody(
            [
                dbc.Label("Select Map Types:"),
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
                dbc.Button(
                    "Revoke Consent",
                    id="revoke-consent",
                    style={"marginTop": "10px"},
                )
            ]
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-settings", className="ml-auto")
        ),
        ],
        id="settings_modal",
    )
