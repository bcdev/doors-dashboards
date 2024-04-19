import sys

import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import yaml
import os
import webbrowser

from flask import request
from waitress import serve

from doors_dashboards.dashboards.dashboard import create_dashboard

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

_CONFIGS_PATH = "../../configs"

# Read all config files from _CONFIGS_PATH
config_files = [f for f in os.listdir(_CONFIGS_PATH) if f.endswith('.yml')]


def get_dashboard_ids():
    list_of_ids = [os.path.splitext(config)[0] for config in config_files]
    list_of_ids.remove("tr1")
    return list_of_ids


def create_dashboard_button(dashboard_id):
    return dbc.Button(f"Dashboard {dashboard_id}", id=f"btn-{dashboard_id}",
                      color="primary", className="mr-1")


def open_in_new_tab(url):
    webbrowser.open_new_tab(url)


def serve_layout(dashboard_id):
    config_path = os.path.join(_CONFIGS_PATH, f"{dashboard_id}.yml")
    with open(config_path, "r", encoding="utf-8") as config_stream:
        config = yaml.safe_load(config_stream)
    layout = create_dashboard(config, app).layout
    return layout


@app.callback(
    Output('dummy-output', 'children'),
    [Input(f'btn-{dashboard_id}', 'n_clicks') for dashboard_id in get_dashboard_ids()],
    prevent_initial_call=True
)
def open_dashboard_in_new_tab(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    clicked_btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    dashboard_id = clicked_btn_id.replace('btn-', '')

    if dashboard_id in get_dashboard_ids():
        serve_layout(dashboard_id)
        current_url = request.url_root
        open_in_new_tab(f"{current_url}{dashboard_id}")
    return dash.no_update


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(id='dummy-output', style={'display': 'none'}),
    # Dummy output to trigger the callback
    html.Div(
        [create_dashboard_button(dashboard_id) for dashboard_id in get_dashboard_ids()],
        id='buttons-container')
])


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    prevent_initial_call=True
)
def display_page(pathname):
    if pathname == "/":
        return html.H1("Select a Dashboard")

    dashboard_id = pathname[1:]  # Remove leading '/'
    if dashboard_id in get_dashboard_ids():
        layout = serve_layout(dashboard_id)
        return layout
    else:
        return html.H1(f"Dashboard {dashboard_id} not found")


if __name__ == '__main__':
    serve(app.server, host="0.0.0.0", port=8787)
