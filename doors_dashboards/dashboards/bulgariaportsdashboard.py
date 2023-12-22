from datetime import date, datetime, timedelta
from dash_material_ui import FormLabel, FormControl

from dash import html, Input, Output, dcc
from dash import Dash

from doors_dashboards.components.scattermap import ScatterMapComponent
from doors_dashboards.components.meteogram import MeteogramComponent

DASHBOARD_ID = 'bulgarian_ports'
BULGARIA_PORTS_POINTS = [
    (27.479, 42.486, 'Terminal East'),
    (27.47, 42.486, 'Terminal Bulk Cargoes'),
    (27.467, 42.48, 'Terminal 2A'),
    (27.457, 42.485, 'Terminal West'),
    (27.53, 42.45, 'Terminal Rosenets'),
    (27.728, 42.657, 'Terminal Nessebar'),
    (27.687, 42.42, 'Terminal Sozopol')
]
METEROGRAM_ID = 'ecmwf-img'

external_stylesheets = ['style.css']

def _create_app() -> Dash:
    app = Dash(__name__,external_stylesheets=external_stylesheets)

    scattermap = ScatterMapComponent().get(DASHBOARD_ID, BULGARIA_PORTS_POINTS)
    coastline_central = BULGARIA_PORTS_POINTS[0]
    marker_label_default = coastline_central[2]
    meteogram = MeteogramComponent().get(coastline_central[0], coastline_central[1])
    current_date = datetime.now().date()
    min_date_allowed = current_date - timedelta(days=10)
    max_date_allowed = current_date

    app.layout = html.Div(
        [
            html.Link(
                rel='stylesheet',
                href='/dashboards/style.css'  # Update the path accordingly
            ),
            # Header Div
            html.Div(
                [
                    html.Img(src='https://doors.viewer.brockmann-consult.de/config/logo.png', style={'width': '200px'}),
                    FormLabel("Burgas Port Dashboard",
                              style={'marginRight': '100px', 'fontSize': '50px','color':'white'}),
                ],

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
                            FormLabel("Select Date: ",   style= { 'marginRight': '10px','fontSize': 'x-large','fontWeight':'bold' }),
                            dcc.DatePickerSingle(
                                id='my-date-picker-single',
                                min_date_allowed=min_date_allowed,
                                max_date_allowed=max_date_allowed,
                                initial_visible_month=current_date,
                                date=current_date,
                               # className =date_picker_style
                            ),
                            FormLabel("Select Wave Type: ", style={'marginLeft': '10px','fontSize': 'x-large','fontWeight':'bold'}),
                            dcc.Dropdown(
                                id='my-dropdown',
                                options=[
                                    {'label': 'classical_10d', 'value': 'classical_10d'},
                                    {'label': 'classical_15d', 'value': 'classical_15d'},
                                    {'label': 'classical_15d_with_climate', 'value': 'classical_15d_with_climate'},
                                    {'label': 'classical_plume', 'value': 'classical_plume'},
                                    {'label': 'classical_wave', 'value': 'classical_wave'},
                                ],
                                value='classical_wave',  # Default selected value
                                style={'width': '230px', 'marginLeft': '10px'}
                            ),
                        ],
                        style={'display': 'flex', 'alignItems': 'center', 'padding': '10px 0px 0px 30px'}
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
                                    'color': 'rgba(0, 0, 0, 0.54)',
                                    'fontSize': 'x-large',
                                    'fontFamily': 'Roboto, Helvetica, Arial, sans-serif',
                                    'fontWeight':'bold'
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
            # Footer
            html.Footer(
                style={'backgroundColor': 'rgb(12, 80, 111)', 'color': 'white', 'padding': '10px',
                       'position': 'fixed',
                       'bottom': '0', 'width': '100%'},
                children=[
                    html.P('© 2023 Brockmann Consult GmbH. All rights reserved.'),
                ]
            ),
        ],
        style={'backgroundColor': 'aliceblue', 'height': '100vh', 'width': '100%' }
    )

    @app.callback(
        Output(METEROGRAM_ID, 'children'),
        Input(DASHBOARD_ID, 'clickData'),
        Input('my-date-picker-single', 'date'),
        Input('my-dropdown', 'value')
    )
    def update_ecmwf_image(click_data, date_value, selected_dropdown_value):
        if date_value is not None and click_data is None and selected_dropdown_value != 'classical_wave':
            marker_label = marker_label_default
            date_object = date.fromisoformat(date_value)
            date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
            return marker_label, MeteogramComponent().get(coastline_central[0], coastline_central[1],
                                                          date_string, selected_dropdown_value)
        elif date_value is None and click_data is None and selected_dropdown_value != 'classical_wave':
            marker_label = marker_label_default
            return marker_label, MeteogramComponent().get(coastline_central[0], coastline_central[1],
                                                          None, selected_dropdown_value)
        elif date_value is not None and click_data is None and selected_dropdown_value == 'classical_wave':
            marker_label = marker_label_default
            date_object = date.fromisoformat(date_value)
            date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
            return marker_label, MeteogramComponent().get(coastline_central[0], coastline_central[1],
                                                          date_string)
        elif click_data is not None:
            marker_label = click_data['points'][0]['text']
            if date_value is not None and selected_dropdown_value != 'classical_wave':
                date_object = date.fromisoformat(date_value)
                date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
                return marker_label, MeteogramComponent().get(click_data['points'][0]['lon'],
                                                              click_data['points'][0]['lat'], date_string,
                                                              selected_dropdown_value)
            elif selected_dropdown_value == 'classical_wave' and date_value is not None:
                date_object = date.fromisoformat(date_value)
                date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
                return marker_label, MeteogramComponent().get(click_data['points'][0]['lon'],
                                                              click_data['points'][0]['lat'], date_string,
                                                              selected_dropdown_value)
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