from dash import Dash, dcc, html
import dash
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/')

layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dcc.Interval(id="image-interval", interval=3000, n_intervals=0),
            html.Img(id="image-slider", src="/assets/image_1.png", style={"width":
                                                                           "800px"}),
        ])
    ),
])


