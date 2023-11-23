import pandas as pd
from dash import html, dcc, Output, Input
from dash import Dash
from doors_dashboards.core.geodbaccess import get_points_from_geodb
from doors_dashboards.components.geodatascattermap import GeoScatterMapComponent

DASHBOARD_ID = 'bulgarian_optical_data'


def _create_app() -> Dash:
    app = Dash(__name__,suppress_callback_exceptions=True)

    points = get_points_from_geodb(
        'bio-optical-data-K11_2019', 'io-bas',
        variables=['chl-a [mg/m3]', 'temperature [°c]', 'salinity [psu]', 'secchi disk [m]', 'timestamp']
    )

    variables = ['chl-a [mg/m3]', 'temperature [°c]', 'salinity [psu]', 'secchi disk [m]']
    selected_variable_default = variables[0]

    scattermap = GeoScatterMapComponent().get(DASHBOARD_ID, points, selected_variable_default)

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
                            html.Div("Select Type: ",
                                     style={'fontSize': 'large', 'fontWeight': 'bold', 'paddingRight': '10px',
                                            'paddingLeft': '10px',
                                            'fontFamily': 'Roboto, Helvetica, Arial, sans-serif'}),
                            dcc.Dropdown(
                                id='variable-dropdown',
                                options=[
                                    {'label': variable, 'value': variable} for variable in variables
                                ],
                                value=selected_variable_default,
                                style={'width': '300px', 'height': '30px'}
                            )
                        ]
                    ),
                    # Map
                    html.Div(
                        id=DASHBOARD_ID,
                        children=[
                            # Map Div
                            scattermap,
                        ]
                    ),
                ],
                style={
                    'display': 'flex',
                    'flexDirection': 'column',  # Adjust to column layout
                    'width': '100%',
                    'height': '100vh',
                }
            ),
        ]
    )

    @app.callback(
        Output(DASHBOARD_ID, 'children'),
        [Input('variable-dropdown', 'value')]
    )
    def update_scattermap(selected_variable):
        print(selected_variable)
        if selected_variable != 'chl-a [mg/m3]':
            updated_scattermap = GeoScatterMapComponent().get(DASHBOARD_ID, points, selected_variable)
            return updated_scattermap
        else:
            print('default', selected_variable_default)
            return GeoScatterMapComponent().get(DASHBOARD_ID, points, selected_variable_default)

    return app


if __name__ == '__main__':
    app = _create_app()
    app.run_server(debug=True)
