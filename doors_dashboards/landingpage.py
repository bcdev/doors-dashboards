import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import os
import doors_dashboards.components.imprintmodal as imprint_modal
from waitress import serve

from doors_dashboards.components.constant import FONT_COLOR
from doors_dashboards.components.mapstyle import popup, SELECT_MAPSTYLE_DRP

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
]

MAPSTYLE_STORE = "mapstyle_value_store"

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True,
           external_stylesheets=external_stylesheets,
           meta_tags=[
               {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])

footer = html.Div(html.P(
    "© 2024 Brockmann Consult GmbH. All rights reserved.",
    className="text-center text-primary",
    style={'color': FONT_COLOR})
)

header = html.Nav(
    className="navbar",
    children=[
        html.A(
            className="navbar-brand",
            href="#",
            children=[
                html.I(
                    className="fas fa-bars",
                    id="open-offcanvas",
                    n_clicks=0,
                    style={"fontSize": "24px", "cursor": "pointer",
                           "marginLeft": "19px", "color": "white"}
                ),
                html.Img(
                    src="../../assets/logo.png",
                    alt="Logo",
                    style={"width": "100px", "paddingTop": "0px", "marginLeft": "10px"}
                )
            ]
        ),
        # Spacer div to push the buttons to the right
        html.Div(style={"flex": "1"}),
        # Grouping settings button and imprint icon
        html.Div(
            children=[
                html.Button(
                    className="btn btn-outline-primary",
                    type="button",
                    id="open-popup",
                    n_clicks=0,
                    children=[
                        html.I(className="fas fa-cogs")
                    ],
                    title="Change map theme",
                    style={"color": "white", "border": "none", "marginRight": "10px"},
                ),
                html.I(
                    className="fa fa-shield-alt",
                    id="open-imprint",
                    n_clicks=0,
                    title="Imprint",
                    style={"cursor": "pointer", "color": "white", "marginRight": "10px"}
                )
            ],
            style={"display": "flex", "alignItems": "center"},
            id="settings-group"
        )
    ],
    style={"display": "flex", "backgroundColor": "rgb(67, 91, 102)", "height": "40px",
           "padding": "0"}
)

offcanvas = html.Div(
    [
        dbc.Offcanvas(
            [
                html.Hr(),
                html.Div([
                    html.Div(
                        dbc.Button(f"{page['name']}",
                                   href=page["relative_path"], color="#77ABB7",
                                   style={"width": "80%"},
                                   className="mb-2")
                    ) for page in dash.page_registry.values()
                ]),
                html.Div(
                    dbc.Button(
                        "Kassandra",
                        href="http://kassandra.ve.ismar.cnr.it:8080/kassandra/black-sea",
                        color="#77ABB7",
                        style={"width": "80%"},
                        className="mb-2",
                        target="_blank"  # Open in a new tab
                    ),
                )
            ],
            id="offcanvas",
            title=html.Img(src="../../assets/logo.png", style={"height": "80px",
                                                               "width": "300px",
                                                               "marginLeft": "-17px"}),
            is_open=False,
            style={"zIndex": 1050, "backgroundColor": "#435B66", "color": "white",
                   "width": "330px"}
        ),
    ],
)


@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    State("offcanvas", "is_open")
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("modal", "is_open"),
    Input("open-popup", "n_clicks"),
    prevent_initial_call=True
)
def open_popup(n_clicks):
    if n_clicks:
        return True
    return False


@app.callback(
    Output(MAPSTYLE_STORE, "data", allow_duplicate=True),
    [Input(SELECT_MAPSTYLE_DRP, "value")],
    prevent_initial_call=True
)
def update_mapstyle_store(value):
    if value:
        mapstyle_value = {
            "mapstyle": value
        }
        return mapstyle_value
    else:
        return dash.no_update


@app.callback(
    Output("scattermap", 'figure',
           allow_duplicate=True),
    [Input(MAPSTYLE_STORE, "data")],
    State('scattermap', 'figure'),
    prevent_initial_call=True
)
def update_mapstyle_of_scattermap(mapstyle_data, current_figure):
    if "mapstyle" in mapstyle_data:
        mapstyle_val = mapstyle_data["mapstyle"]

        if mapstyle_val is not None:
            if isinstance(current_figure, dict) and "data" in current_figure:
                current_figure = go.Figure(current_figure)
                if "accesstoken" not in current_figure.layout.mapbox:
                    current_figure.layout.mapbox[
                        "accesstoken"] = \
                        "pk.eyJ1Ijoicm1vdHdhbmkiLCJhIjoiY2xvNDVndHY2MDRlejJ4czIwa3QyYnk2bCJ9.g88Jq0lCZRcQda4eNPks2Q"
                current_figure.layout.mapbox["style"] = mapstyle_val

                return current_figure
    return current_figure


@app.callback(
    Output("modal-imprint", "is_open"),
    [Input("open-imprint", "n_clicks"),
     Input("close-imprint", "n_clicks")],
    [State("modal-imprint", "is_open")]
)
def toggle_imprint_modal(open_click, close_click, is_open):
    if open_click or close_click:
        return not is_open
    return is_open


@app.callback(
    Output("open-popup", "style"),
    Input("url", "pathname")
)
def hide_settings_on_home(pathname):
    if pathname == "/":
        return {"display": "none"}
    return {"display": "flex", "alignItems": "center"}


app.layout = dbc.Container(
    [
        dcc.Location(id="url"),
        dcc.Store(id=MAPSTYLE_STORE),
        header,
        dbc.Row(
            dash.page_container,
            style={"backgroundColor": "#2D4356"}),
        dbc.Row([offcanvas]),
        dbc.Row([footer], style={"backgroundColor": "#2D4356", "flex": "0 1 auto"}),
        popup,
        imprint_modal.ImprintModal()
    ],
    fluid=True,
    style={"padding": "0", "display": "flex",
           "flexDirection": "column"},
    className="container scalable"
)

if __name__ == '__main__':
    serve(app.server, host="0.0.0.0", port=8789)
