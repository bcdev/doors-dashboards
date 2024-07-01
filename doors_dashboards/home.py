import dash
from dash import html
import dash_bootstrap_components as dbc

from doors_dashboards.components.constant import FONT_COLOR


def register_homepage():

    hero_content = {
        "image": "/assets/dashboard_img.png",
        "title": "Unleash the Power of Your Data",
        "desc": (
            "The DOORS Dashboard Application provides users with an intuitive and visually "
            "engaging interface for exploring and analyzing diverse datasets through "
            "interactive visuals. It enables users to easily interpret data without "
            "needing prior knowledge of the platform. The application features a range of "
            "functionalities, from weather forecasts and time series to scatter plots like"
            " point and line graphs, along with trajectory presentations, all accessible "
            "from its dashboard. "
            "Its lightweight design ensures"
            " quick load times and seamless user interactions, "
            "enhancing the overall user experience."
        ),
    }

    layout = dbc.Container(
        [
            html.Div(
                style={"display": "flex", "align-items": "center"},
                children=[
                    html.Img(src="/assets/dashboard_img.png", style={"width": "600px"}),
                    html.Div(
                        style={"width": "50%", "padding": "15px"},
                        children=[
                            html.Div(
                                children=[
                                    html.Img(
                                        src="/assets/logo.png", style={"width": "600px"}
                                    ),
                                    html.H2(
                                        children=html.Span(
                                            hero_content["title"],
                                            style={"color": FONT_COLOR},
                                        )
                                    ),
                                    html.P(
                                        children=hero_content["desc"],
                                        style={"color": FONT_COLOR},
                                    ),
                                ]
                            )
                        ],
                    ),
                ],
            )
        ],
        fluid=True,
    )

    dash.register_page(__name__, path="/", layout=layout)
