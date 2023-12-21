from dash import html, dcc, Output, Input
from dash import Dash
from dash_material_ui import FormLabel

from doors_dashboards.core.geodbaccess import get_points_from_geodb, get_dataframe_from_geodb
from doors_dashboards.components.geodatascattermap import GeoScatterMapComponent
from doors_dashboards.components.timeseries import TimeSeriesComponent

DASHBOARD_ID = 'Geodb_optical_data'
MAP_ID = 'geodb_data'
TIMESERIES_ID = 'geo_timeseries'
TIMEGRAPH_ID = 'geo_graph'


def _create_app() -> Dash:
    app = Dash(__name__, suppress_callback_exceptions=True)

    variables = ['wind speed [m/s]', 'wind direction [deg]', 'significant wave height [m]']
    selected_variable_default = variables[0]

    points = get_points_from_geodb('moorings_Burgas_Bay_wavebuoy', 'doors-io-bas',
                                   variables=variables)

    dataframe = get_dataframe_from_geodb('moorings_Burgas_Bay_wavebuoy', 'doors-io-bas',
                                         variables=variables)

    scattermap = GeoScatterMapComponent().get(DASHBOARD_ID, points, selected_variable_default)
    timeseries = TimeSeriesComponent().get(dataframe, variables, TIMESERIES_ID)

    app.layout = html.Div(
        [
            # Header Div
            html.Div(
                html.Img(src='https://doors.viewer.brockmann-consult.de/config/logo.png', style={'width': '200px'}),
                style={
                    'backgroundColor': 'rgb(12, 80, 111)',
                    'padding': '15px',
                    'textAlign': 'left',
                }
            ),

            # Main content Div
            html.Div(
                children=[
                    # Date Picker Div
                    html.Div(
                        [
                            FormLabel("Select Type: ", style={ 'fontSize': 'larger'}),
                            dcc.Dropdown(
                                id='variable-dropdown',
                                options=[
                                    {'label': variable, 'value': variable} for variable in variables
                                ],
                                value=selected_variable_default,
                                style={'width': '300px', 'height': '30px'}
                            )
                        ]
                        , style={
                            'padding': '7px 0px 0px 36px'
                        }
                    ),
                    html.Div(
                        [
                            # Map
                            html.Div(
                                id=MAP_ID,
                                children=[
                                    # Map Div
                                    scattermap,
                                ], style={
                                    'width': '100%',
                                    'paddingTop': '20px'
                                }
                            ),
                            html.Div(
                                id=TIMEGRAPH_ID,
                                children=[
                                    # Map Div
                                    timeseries,
                                ], style={
                                    'width': '100%',
                                    'paddingTop': '20px',

                                }
                            ),
                        ],
                        style={'display': 'flex'}
                    ),
                ],
                style={
                    'display': 'flex',
                    'flexDirection': 'column',  # Adjust to column layout
                    'width': '100%',
                    'height': '100vh',
                    'backgroundColor': 'rgb(228, 241, 245)',
                }
            ),
        ],
        style={
            'width': '100%',
            'height': '100vh'
        }
    )

    @app.callback(
        [Output(MAP_ID, 'children'), Output(TIMEGRAPH_ID, 'children')],
        [Input('variable-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_scattermap(selected_variable):
        if selected_variable != variables[0]:
            updated_scattermap = GeoScatterMapComponent().get(DASHBOARD_ID, points, selected_variable)
            updated_timeseries = TimeSeriesComponent().get(dataframe, selected_variable, TIMESERIES_ID)
            return updated_scattermap, updated_timeseries
        else:
            return (GeoScatterMapComponent().get(DASHBOARD_ID, points, selected_variable_default),
                    TimeSeriesComponent().get(dataframe, selected_variable_default, TIMESERIES_ID))

    return app


if __name__ == '__main__':
    app = _create_app()
    app.run_server(debug=True)
