import dash_bootstrap_components as dbc
from dash import html


def create_consent_modal():
    return dbc.Modal([
        dbc.ModalBody(html.Div([
            html.H4("Privacy Notice"),
            html.P(
                "Before you continue, you should know "
                "the following about this application:"
            ),
            html.Ul([
                html.Li(
                    "This application obtains its data from application servers "
                    "of Brockmann Consult GmbH."),
                html.Li("Free third-party map services are used."),
                html.Li("No user data is collected or shared."),
                html.Li([
                    "Application settings are stored in the browser's local memory. ",
                    html.A("(HTML5 local storage)",
                            href="https://en.wikipedia.org/wiki/Web_storage",
                            target="_blank"),
                    ])
                ]),
                html.P(
                    "You can revoke your consent in the system settings at any time.")
            ])),
        dbc.ModalFooter([
            dbc.Button(
                "I Consent", id="accept-cookies", className="ms-auto", n_clicks=0
            ),
            dbc.Button(
                "I Do Not Consent", id="decline-cookies",
                className="ms-auto", n_clicks=0
            )]),
        ],
        id="consent_modal",
        is_open=False,
    )
