import dash
from dash import html
import dash_bootstrap_components as dbc

from doors_dashboards.components.constant import FONT_COLOR


def register_homepage():

    hero_content = {
        "image": "/assets/dashboard_img.png",
        "title": "Dear Ruchi",
        "desc": (
            "I wish you all the best for the future. I hope that the things you have "
            "learnt and the expericences you have made at your time a BC will be of "
            "worth to you. Also, I hope that whatever you do next will work out for "
            "you and you find a place where you can show your qualities and they are "
            "appreciated. It was good working with you. You were of help. We couldn't "
            "have achieved what we did without you. Thank you and goodbye!"
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
