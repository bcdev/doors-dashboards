from datetime import date, datetime, timedelta

from dash import html, Input, Output, dcc
from dash import Dash

from doors_dashboards.components.scattermap import ScatterMapComponent
from doors_dashboards.components.meteogram import MeteogramComponent

DASHBOARD_ID = 'RO1'
ROMANIA_POINTS = [
    (29.66, 45.19, 'Golful Musura'),
    (29.05, 44.6, 'Danube Delta'),
    (28.7, 44.15, 'Constanța')
]
METEOGRAM_ID = 'ecmwf-img'


def create_dashboard() -> Dash:
    app = Dash(__name__)

    scattermap = ScatterMapComponent().get(DASHBOARD_ID, ROMANIA_POINTS)
    coastline_central = ROMANIA_POINTS[0]
    marker_label_default = coastline_central[2]
    meteogram = MeteogramComponent().get(
        coastline_central[0], coastline_central[1]
    )
    current_date = datetime.now().date()
    min_date_allowed = current_date - timedelta(days=10)
    max_date_allowed = current_date

    app.layout = html.Div(
        [
            # Header Div
            html.Div(
                html.Img(src="assets/logo.png", style={'width': '200px'}),
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
                            html.Div("Date: ",
                                     style={
                                         'fontSize': 'large',
                                         'fontWeight': 'bold',
                                         'paddingRight': '10px',
                                         'paddingLeft': '10px',
                                         'fontFamily': 'Roboto, Helvetica, '
                                                       'Arial, sans-serif'}
                                     ),
                            dcc.DatePickerSingle(
                                id='my-date-picker-single',
                                min_date_allowed=min_date_allowed,
                                max_date_allowed=max_date_allowed,
                                initial_visible_month=current_date,
                                date=current_date
                            ),
                            html.Div("Forecast: ",
                                     style={'fontSize': 'large',
                                            'fontWeight': 'bold',
                                            'paddingRight': '10px',
                                            'paddingLeft': '45px',
                                            'fontFamily': 'Roboto, Helvetica, '
                                                          'Arial, sans-serif'}
                                     ),
                            dcc.Dropdown(
                                id='my-dropdown',
                                options=[
                                    {'label': 'classical_10d',
                                     'value': 'classical_10d'},
                                    {'label': 'classical_15d',
                                     'value': 'classical_15d'},
                                    {'label': 'classical_15d_with_climate',
                                     'value': 'classical_15d_with_climate'},
                                    {'label': 'classical_plume',
                                     'value': 'classical_plume'},
                                    {'label': 'classical_wave',
                                     'value': 'classical_wave'},
                                ],
                                value='classical_wave',  # default value
                                style={'width': '230px', 'marginLeft': '10px'}
                            ),
                        ],
                        style={
                            'display': 'flex', 'alignItems': 'center',
                            'paddingTop': '10px'
                        }
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
                                id=METEOGRAM_ID,
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
                                    'fontFamily': 'Roboto, Helvetica, '
                                                  'Arial, sans-serif'
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
        Output(METEOGRAM_ID, 'children'),
        Input(DASHBOARD_ID, 'clickData'),
        Input('my-date-picker-single', 'date'),
        Input('my-dropdown', 'value')
    )
    def update_ecmwf_image(click_data, date_value, selected_dropdown_value):
        if date_value is not None and click_data is None \
                and selected_dropdown_value != 'classical_wave':
            marker_label = marker_label_default
            date_object = date.fromisoformat(date_value)
            date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
            return marker_label, MeteogramComponent().get(
                coastline_central[0], coastline_central[1], date_string,
                selected_dropdown_value
            )
        elif date_value is None and click_data is None \
                and selected_dropdown_value != 'classical_wave':
            marker_label = marker_label_default
            return marker_label, MeteogramComponent().get(
                coastline_central[0], coastline_central[1], None,
                selected_dropdown_value
            )
        elif date_value is not None and click_data is None \
                and selected_dropdown_value == 'classical_wave':
            marker_label = marker_label_default
            date_object = date.fromisoformat(date_value)
            date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
            return marker_label, MeteogramComponent().get(
                coastline_central[0], coastline_central[1], date_string
            )
        elif click_data is not None:
            marker_label = click_data['points'][0]['text']
            if date_value is not None \
                    and selected_dropdown_value != 'classical_wave':
                date_object = date.fromisoformat(date_value)
                date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
                return marker_label, MeteogramComponent().get(
                    click_data['points'][0]['lon'],
                    click_data['points'][0]['lat'],
                    date_string,selected_dropdown_value
                )
            elif selected_dropdown_value == 'classical_wave' \
                    and date_value is not None:
                date_object = date.fromisoformat(date_value)
                date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
                return marker_label, MeteogramComponent().get(
                    click_data['points'][0]['lon'],
                    click_data['points'][0]['lat'],
                    date_string, selected_dropdown_value
                )
            else:
                return marker_label, MeteogramComponent().get(
                    click_data['points'][0]['lon'],
                    click_data['points'][0]['lat']
                )
        else:
            marker_label = marker_label_default
            return marker_label, meteogram

    return app


if __name__ == '__main__':
    dashboard = create_dashboard()
    dashboard.run_server(debug=True)
