import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

from doors_dashboards.components.constant import FONT_COLOR
from doors_dashboards.components.mapstyle import popup, SELECT_MAPSTYLE_DRP

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
]

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True,
           external_stylesheets=external_stylesheets)

footer = html.Div(html.P(
    "© 2024 Brockmann Consult GmbH. All rights reserved.",
    className="text-center text-primary",
    style={'color': FONT_COLOR})
)

header = dbc.Row(
    [
        dbc.Col(
            html.I(className="fas fa-bars", id="open-offcanvas", n_clicks=0,
                   style={"fontSize": "24px", "cursor": "pointer", "margin-left":
                       "19px", "padding-top": "10px", }),
            width="auto",
        ),
        dbc.Col(html.Img(src="../../assets/logo.png", style={'width': '100px',
                                                             'paddingTop': '16px'}),
                width="auto"),
        dbc.Col(
            dbc.Button(html.I(className="fas fa-cogs"), id="open-popup",
                       n_clicks=0, color="primary", outline=True, style={
                }),
            width="auto"
        ),
        dbc.Col(
            dash.page_container,
            width={"size": 12},
            # style={"margin": "-60px 0 75px 18px"}
        ),

    ],
    style={"alignItems": "center", "backgroundColor": "#2D4356"}
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
            ],
            id="offcanvas",
            title=html.Img(src="../../assets/logo.png", style={"height": "80px",
                                                               "width": "300px",
                                                               "marginLeft":"-17px"}),
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
    Output("dropdown-value", "children"),
    [Input(SELECT_MAPSTYLE_DRP, "value")]
)
def update_dropdown_value(value):
    if value:
        return print(f"You selected: {value}")
    else:
        return ""


app.layout = dbc.Container(
    [
        dbc.Row([header], style={"backgroundColor": "#2D4356", "flex": "0 1 auto"}),
        dbc.Row([offcanvas]),
        dbc.Row([footer], style={"backgroundColor": "#2D4356", "flex": "0 1 auto"}),
        popup
    ],
    fluid=True,
    style={"height": "100vh", "padding": "0", "display": "flex", "flexDirection":
        "column"}

)

if __name__ == '__main__':
    app.run_server(debug=True)
