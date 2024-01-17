from dash import Dash
from dash import html
from dash import Input
from dash import Output
from dash_material_ui import FormLabel
from dash.exceptions import PreventUpdate
import pandas as pd

from doors_dashboards.core.geodbaccess import get_dataframe_from_geodb
from doors_dashboards.core.geodbaccess import get_points_from_geodb
from doors_dashboards.components.geodatascattermap import GeoScatterMapComponent
from doors_dashboards.components.timeseries import TimeSeriesComponent
from doors_dashboards.components.timeslider import TimeSliderComponent

DASHBOARD_ID = 'Geodb_optical_data'
MAP_ID = 'geodb_data'

WINDSPEED_ID = 'windspeed_timeseries'
WINDDIRECTION_ID = 'winddirection_timeseries'
WAVEHEIGHT_ID = 'waveheight_timeseries'
TIMEGRAPHS_ID = 'timegraphs'
TIMEGRAPH_ID = 'geo_graph'
TIMEPLOT_ID = 'timeplot'
TIMESLIDERDIV_ID = 'timeslider_div'
TIMESLIDER_ID = 'timeslider'
COLLECTION_NAME = 'bio-optical-data-K11_2019'
DASHBOARD_TITLE = 'Bio-optical Data K11 2019'
FONT_COLOR = "#cedce2"


def create_dashboard() -> Dash:
    app = Dash(__name__, suppress_callback_exceptions=True)

    variables = [
        'chl-a [mg/m3]', 'temperature [°c]', 'salinity [psu]', 'secchi disk [m]'
    ]
    selected_variable_default = variables[0]

    points = get_points_from_geodb(COLLECTION_NAME, 'io-bas',
                                   variables=variables)

    dataframe = get_dataframe_from_geodb(COLLECTION_NAME, 'io-bas',
                                         variables=variables)

    scattermap = GeoScatterMapComponent().get(
        DASHBOARD_ID, points, selected_variable_default
    )
    line_plots = TimeSeriesComponent().get(dataframe, variables, TIMEPLOT_ID)
    line_slider = TimeSliderComponent().get(dataframe, TIMESLIDER_ID)

    app.layout = html.Div(
        style={
            'height': '80vh',
        },
        children=[
            # Header
            html.Header(
                [
                    html.Img(src="assets/logo.png", style={'width': '200px'}),
                    FormLabel(DASHBOARD_TITLE,
                              style={'fontSize': '-webkit-xxx-large',
                                     'margin': '0 0 0 100px',
                                     'color': FONT_COLOR}
                              )
                ],
                style={
                    "display": "flex",
                    'backgroundColor': 'rgb(12, 80, 111)',
                    'padding': '15px',
                    "alignItems": "left",
                }
            ),
            # Main content with scattermap on the left and graph on the right
            html.Div(
                style={
                    'display': 'flex',
                    'height': '80vh',
                },
                children=[
                    html.Div(
                        id=MAP_ID,
                        children=[
                            # Map Div
                            scattermap,
                        ], style={
                            'width': '50%',
                            'paddingTop': '20px',
                            'height': '90%'
                        }
                    ),
                    html.Div(
                        id = TIMEGRAPHS_ID,
                        children=[
                            html.Div(
                                id=TIMEGRAPH_ID,
                                children=[
                                    line_plots
                                ], style={
                                    "margin": "10px",
                                    "height": "80%"
                                }
                            ),
                            html.Div(
                                id=TIMESLIDERDIV_ID,
                                children=[
                                    line_slider
                                ], style={
                                    "margin": "10px",
                                    "paddingLeft": "6.5%",
                                    "paddingRight": "6.5%",
                                    "height": "10%"
                                }
                            )
                        ], style={
                            'width': '50%',
                            'paddingTop': '20px',
                        }
                    ),
                ]
            ),

            # Footer
            html.Footer(
                style={
                    'backgroundColor': 'rgb(12, 80, 111)', 'color': FONT_COLOR,
                    'padding': '10px', 'position': 'fixed', 'bottom': '0',
                    'width': '100%',
                    'fontFamily': 'Roboto, Helvetica, Arial, sans-serif'
                },
                children=[
                    html.P(
                        '© 2024 Brockmann Consult GmbH. All rights reserved.'
                    ),
                ]
            ),
        ]
    )

    @app.callback(
        Output(TIMEGRAPH_ID, 'children'),
        Input(TIMESLIDER_ID, 'value')
    )
    def update_timeplots(value):
        if value is None:
            raise PreventUpdate
        timestamp_range = [pd.Timestamp.fromordinal(int(v)) for v in value]
        line_plots.figure.update_xaxes(
            range=timestamp_range
        )
        return line_plots

    @app.callback(
        Output(TIMESLIDER_ID, 'value'),
        Input(TIMEPLOT_ID, 'relayoutData')
    )
    def update_timeslider(relayout_data):
        if relayout_data is None or \
                'xaxis.range[0]' not in relayout_data or \
                'xaxis.range[1]' not in relayout_data:
            raise PreventUpdate
        start = pd.Timestamp(relayout_data['xaxis.range[0]']).toordinal()
        end = pd.Timestamp(relayout_data['xaxis.range[1]']).toordinal()
        return [start, end]

    return app


if __name__ == '__main__':
    dashboard = create_dashboard()
    dashboard.run(debug=True)
