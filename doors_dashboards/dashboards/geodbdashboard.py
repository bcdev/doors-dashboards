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
COLLECTION_NAME = 'moorings_Burgas_Bay_wavebuoy'
DASHBOARD_TITLE = 'Moornings Burgas Bay WaveBuoy'


def _create_app() -> Dash:
    app = Dash(__name__, suppress_callback_exceptions=True)

    variables = ['wind speed [m/s]', 'wind direction [deg]', 'significant wave height [m]']
    selected_variable_default = variables[0]

    points = get_points_from_geodb(COLLECTION_NAME, 'doors-io-bas',
                                   variables=variables)

    dataframe = get_dataframe_from_geodb(COLLECTION_NAME, 'doors-io-bas',
                                         variables=variables)

    scattermap = GeoScatterMapComponent().get(DASHBOARD_ID, points, selected_variable_default)
    timeseries = TimeSeriesComponent().get(dataframe, variables, TIMESERIES_ID)

    app.layout = html.Div(
        style={'backgroundColor': 'aliceblue', 'height': '100vh', 'width': '100%', },
        children=[
            # Header
            html.Header(
                html.Img(src='https://doors.viewer.brockmann-consult.de/config/logo.png', style={'width': '200px'}),
                style={
                    'backgroundColor': 'rgb(12, 80, 111)',
                    'padding': '15px',
                    'textAlign': 'left',
                    'width': '100%'
                }
            ),

            # Row below header with dropdown on the left
            html.Header(
                [
                    FormLabel("Select Type: ",
                              style={'fontWeight': 'bold', 'fontSize': 'x-large', 'padding': '6px 0px 0px 0px'}),
                    dcc.Dropdown(
                        id='variable-dropdown',
                        options=[
                            {'label': variable, 'value': variable} for variable in variables
                        ],
                        value=selected_variable_default,
                        style={
                            'width': '300px',  # Set the width as needed
                            'height': '40px',  # Increase the height
                            'fontSize': '16px',
                            'margin': '0 0 0 5px'
                        }
                    ),
                    FormLabel(DASHBOARD_TITLE, style={'fontSize': '-webkit-xxx-large', 'margin': '0 0 0 1000px'})
                ]
                , style={
                    'padding': '20px 0px 0px 36px', 'width': '100%', 'display': 'flex'
                }
            ),

            # Main content with scattermap on the left and graph on the right
            html.Div(
                style={'display': 'flex'},
                children=[
                    html.Div(
                        id=MAP_ID,
                        children=[
                            # Map Div
                            scattermap,
                        ], style={
                            'width': '100%',
                            'paddingTop': '20px',
                            'height': '100vh'
                        }
                    ),
                    html.Div(
                        id=TIMEGRAPH_ID,
                        children=[
                            # Map Div
                            timeseries,
                        ], style={
                            'width': '80%',
                            'paddingTop': '20px',
                            'height': '100vh',
                            'marginBottom': '50px',

                        }
                    ),
                ]
            ),

            # Footer
            html.Footer(
                style={'backgroundColor': 'rgb(12, 80, 111)', 'color': 'white', 'padding': '10px',
                       'position': 'fixed',
                       'bottom': '0', 'width': '100%'},
                children=[
                    html.P('© 2023 Brockmann Consultants. All rights reserved.'),
                ]
            ),
        ]
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
                    TimeSeriesComponent().get(dataframe, variables[0], TIMESERIES_ID))

    return app


if __name__ == '__main__':
    app = _create_app()
    app.run_server(debug=True)
