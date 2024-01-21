from dash import Dash
from dash import dcc
from dash import html
from dash import Input
from dash import Output
from dash.development.base_component import Component
from dash_material_ui import FormLabel
from copy import deepcopy
from datetime import date
from datetime import datetime
from datetime import timedelta
import requests
from typing import Dict
from typing import List

from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

METEOGRAM_ENDPOINT = \
    "https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram/"
HEADERS = {"accept": "application/json"}
BASE_PARAMS = {
    "format": "png"
}

METEOGRAM_IMAGE_ID = "meteogram_image"
METEOGRAM_DATE_PICKER_ID = "meteogram_date_picker"
METEOGRAM_CHOOSER_ID = "meteogram_chooser"


class MeteogramComponent(DashboardComponent):

    def __init__(self):
        self._feature_handler = None
        self._meteogram_image = None

    def get(
            self, sub_component: str, sub_component_id: str, sub_config: Dict
    ) -> Component:
        if sub_component == METEOGRAM_IMAGE_ID:
            self._meteogram_image = self._get_meteogram_image(
                sub_component_id,
                sub_config.get("lon"),
                sub_config.get("lat"),
                sub_config.get("time"),
                sub_config.get("meteogram_type", "classical_wave")
            )
            return self._meteogram_image
        if sub_component == "meteogram_selection":
            return self._get_meteogram_selection()
        raise ValueError(f"Unknown subcomponent {sub_component} passed to "
                         f"'meteogram'. Must be one of 'meteogram_image', "
                         f"'meteogram_selection'.")

    def _get_meteogram_image(self, sub_component_id: str,
                             lon: float, lat: float, time: str = None,
                             meteogram_type: str = 'classical_wave') -> Component:
        params = self._get_params(lon, lat, meteogram_type, time)
        response = requests.get(
            METEOGRAM_ENDPOINT, params=params, headers=HEADERS
        )
        if response.status_code != 200:
            return html.Label(
                f'Meteogram could not be loaded: {response.reason}'
            )
        response_data = response.json()
        image_url = response_data.get('data', {}).get('link', {}).get('href')
        if not image_url:
            return html.Label('Meteogram could not be loaded: '
                              'No image url in reponse from ECMWF')
        meteogram_image = html.Img(src=image_url, style={'padding': '20px'})
        return html.Div(
            id=sub_component_id,
            children=[
                meteogram_image,
            ],
            style={
                'flex': '1',
                'margin': '-34px 0 0 0',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'color': 'rgba(0, 0, 0, 0.54)',
                'fontSize': 'x-large',
                'fontFamily':
                    'Roboto, Helvetica, Arial, sans-serif',
                'fontWeight': 'bold'
            }
        )

    def _get_params(self, lon: float, lat: float,
                    meteogram_type: str = 'classical_wave', time: str = None
                    ) -> Dict[str, str]:
        params = deepcopy(BASE_PARAMS)
        params['lon'] = lon
        params['lat'] = lat
        params['epsgram'] = meteogram_type
        if not time:
            time = datetime.now().strftime('%Y-%m-%dT00:00:00Z')
        params['base_time'] = time
        return params

    def _get_meteogram_selection(self):
        current_date = datetime.now().date()
        min_date_allowed = current_date - timedelta(days=10)
        max_date_allowed = current_date
        return html.Div([
            FormLabel("Select Date: ",
                       style= {'marginRight': '10px',
                               'fontSize': 'x-large','fontWeight':'bold'}
                       ),
             dcc.DatePickerSingle(
                 id=METEOGRAM_DATE_PICKER_ID,
                 min_date_allowed=min_date_allowed,
                 max_date_allowed=max_date_allowed,
                 initial_visible_month=current_date,
                 date=current_date,
             ),
             FormLabel("Select Wave Type: ",
                       style={'marginLeft': '10px',
                              'fontSize': 'x-large',
                              'fontWeight':'bold'}
                       ),
             dcc.Dropdown(
                 id=METEOGRAM_CHOOSER_ID,
                 options=[
                     {'label': 'classical_10d', 'value': 'classical_10d'},
                     {'label': 'classical_15d', 'value': 'classical_15d'},
                     {'label': 'classical_15d_with_climate',
                      'value': 'classical_15d_with_climate'},
                     {'label': 'classical_plume',
                      'value': 'classical_plume'},
                     {'label': 'classical_wave', 'value': 'classical_wave'}
                 ],
                 value='classical_wave',  # Default selected value
                 style={'width': '230px', 'marginLeft': '10px'}
             ),
        ],
            style={'display': 'flex',
                   'alignItems': 'center',
                   'padding': '10px 0px 0px 30px'
                   }
        )

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self._feature_handler = feature_handler

    def register_callbacks(self, app: Dash, component_ids: List[str]):
        if "scattermap" not in component_ids:
            return

        points = self._feature_handler.get_points_as_tuples()
        lon = points[0]
        lat = points[1]
        label = points[1]

        @app.callback(
            Output(METEOGRAM_IMAGE_ID, 'children'),
            Input("scattermap", 'clickData'),
            Input(METEOGRAM_DATE_PICKER_ID, 'date'),
            Input(METEOGRAM_CHOOSER_ID, 'value')
        )
        def update_ecmwf_image(click_data, date_value, selected_dropdown_value):
            if date_value is not None and click_data is None \
                    and selected_dropdown_value != 'classical_wave':
                marker_label = label
                date_object = date.fromisoformat(date_value)
                date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
                return marker_label, self._get_meteogram_image(
                    METEOGRAM_IMAGE_ID, lon, lat, date_string,
                    selected_dropdown_value
                )
            elif date_value is None and click_data is None \
                    and selected_dropdown_value != 'classical_wave':
                marker_label = label
                return marker_label, self._get_meteogram_image(
                    METEOGRAM_IMAGE_ID, lon, lat, None, selected_dropdown_value
                )
            elif date_value is not None and click_data is None and \
                    selected_dropdown_value == 'classical_wave':
                marker_label = label
                date_object = date.fromisoformat(date_value)
                date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
                return marker_label, self._get_meteogram_image(
                    METEOGRAM_IMAGE_ID, lon, lat, date_string
                )
            elif click_data is not None:
                marker_label = click_data['points'][0]['text']
                if date_value is not None \
                        and selected_dropdown_value != 'classical_wave':
                    date_object = date.fromisoformat(date_value)
                    date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
                    return marker_label, self._get_meteogram_image(
                        METEOGRAM_IMAGE_ID,
                        click_data['points'][0]['lon'],
                        click_data['points'][0]['lat'],
                        date_string, selected_dropdown_value
                    )
                elif selected_dropdown_value == 'classical_wave' \
                        and date_value is not None:
                    date_object = date.fromisoformat(date_value)
                    date_string = date_object.strftime('%Y-%m-%dT00:00:00Z')
                    return marker_label, self._get_meteogram_image(
                        METEOGRAM_IMAGE_ID,
                        click_data['points'][0]['lon'],
                        click_data['points'][0]['lat'],
                        date_string, selected_dropdown_value
                    )
                else:
                    return marker_label, self._get_meteogram_image(
                        METEOGRAM_IMAGE_ID,
                        click_data['points'][0]['lon'],
                        click_data['points'][0]['lat']
                    )
            else:
                marker_label = label
                return marker_label, self._meteogram_image
