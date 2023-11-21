from datetime import date, datetime, timedelta

from dash import html, Input, Output, dcc
from dash import Dash

from doors_dashboards.components.scattermap import ScatterMapComponent
from doors_dashboards.components.meteogram import MeteogramComponent

DASHBOARD_ID = 'bulgarian_ports'
ROMANIA_POINTS = [
    (29.66, 45.19, 'Golful Musura'),
    (29.05, 44.6, 'Danube Delta'),
    (28.7, 44.15, 'Constanța')
]
METEROGRAM_ID = 'ecmwf-img'


def _create_app() -> Dash:
    app = Dash(__name__)

    scattermap = ScatterMapComponent().get(DASHBOARD_ID, ROMANIA_POINTS)
    coastline_central = ROMANIA_POINTS[0]
    marker_label_default = coastline_central[2]
    meteogram = MeteogramComponent().get(coastline_central[0], coastline_central[1])
    current_date = datetime.now().date()
    min_date_allowed = current_date - timedelta(days=10)
    max_date_allowed = current_date

    app.layout = html.Div(
        [
            # Header Div
            html.Div(
                html.Img(src='https://doors.viewer.brockmann-consult.de/config/logo.png',style={'width': '200px'}),
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
                            html.Div("Select date: ", style={'fontSize': 'large', 'fontWeight': 'bold', 'paddingRight': '10px', 'fontFamily': 'Roboto, Helvetica, Arial, sans-serif' }),
                            dcc.DatePickerSingle(
                                id='my-date-picker-single',
                                min_date_allowed=min_date_allowed,
                                max_date_allowed=max_date_allowed,
                                initial_visible_month=current_date,
                                date=current_date
                            ),
                        ],
                        style={'display': 'flex', 'alignItems': 'center', 'paddingLeft': '300px', 'paddingTop': '10px'}
                    ),

                    # Map and Meteogram Divs side by side
                    html.Div(
                        children=[
                            # Map Div
                            html.Div(
                                scattermap,
                                style={
                                    'flex': '1',
                                    'margin': '10px',
                                    'alignItems': 'center',
                                }
                            ),

                            # Meteogram Div
                            html.Div(
                                id=METEROGRAM_ID,
                                children=[
                                    meteogram,
                                ],
                                style={
                                    'flex': '1',
                                    'margin': '-34px 0 0 0',
                                    'display': 'flex',
                                    'flexDirection': 'column',
                                    'alignItems': 'center',
                                    'fontSize': 'xx-large',
                                    'fontWeight': 'bold',
                                    'color': 'black',
                                    'fontFamily': 'Roboto, Helvetica, Arial, sans-serif'
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
                }
            ),
        ]
    )

    @app.callback(
        Output(METEROGRAM_ID, 'children'),
        Input(DASHBOARD_ID, 'clickData'),
        Input('my-date-picker-single', 'date')
    )
    def update_ecmwf_image(click_data, date_value):
        if date_value is not None and click_data is None:
            marker_label = marker_label_default
            date_object = date.fromisoformat(date_value)
            date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
            return marker_label, MeteogramComponent().get(coastline_central[0], coastline_central[1],
                                                          date_string)
        elif click_data is not None:
            marker_label = click_data['points'][0]['text']
            if date_value is not None:
                date_object = date.fromisoformat(date_value)
                date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
                return marker_label, MeteogramComponent().get(click_data['points'][0]['lon'],
                                                              click_data['points'][0]['lat'], date_string)
            else:
                return marker_label, MeteogramComponent().get(click_data['points'][0]['lon'],
                                                              click_data['points'][0]['lat'])
        else:
            marker_label = marker_label_default
            return marker_label, meteogram

    return app


if __name__ == '__main__':
    app = _create_app()
    app.run_server(debug=True)
