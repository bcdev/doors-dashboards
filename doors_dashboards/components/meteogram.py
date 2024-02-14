from dash import dcc, html, Input, Output, dash
from dash.development.base_component import Component
from copy import deepcopy
from datetime import date
from datetime import datetime
from datetime import timedelta
import requests
from typing import Dict
from typing import List
from typing import Tuple
import dash_bootstrap_components as dbc

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
        self._default_tuple = None
        self._feature_handler = None
        self._meteogram_image = None
        self._previous_images = dict()

    def get(
            self, sub_component: str, sub_component_id: str, sub_config: Dict
    ) -> Component:
        if sub_component == METEOGRAM_IMAGE_ID:
            default_lon, default_lat, _ = self._get_default_tuple()
            self._meteogram_image = self._get_wrapped_meteogram_image(
                sub_component_id,
                sub_config.get("lon", default_lon),
                sub_config.get("lat", default_lat),
                sub_config.get("time"),
                sub_config.get("meteogram_type", "classical_wave")
            )
            return self._meteogram_image
        if sub_component == "meteogram_selection":
            return self._get_meteogram_selection()
        raise ValueError(f"Unknown subcomponent {sub_component} passed to "
                         f"'meteogram'. Must be one of 'meteogram_image', "
                         f"'meteogram_selection'.")

    def _get_default_tuple(self) -> Tuple[float, float, str]:
        if not self._default_tuple:
            collection = self._feature_handler.get_collections()[0]
            points = self._feature_handler.get_points_as_tuples(collection)
            lon = points[0][0]
            lat = points[1][0]
            label = points[2][0]
            self._default_tuple = lon, lat, label
        return self._default_tuple

    def _get_wrapped_meteogram_image(
            self, sub_component_id: str, lon: float, lat: float,
            time: str = None, meteogram_type: str = 'classical_wave'
    ) -> Component:
        meteogram_image = self._get_meteogram_image(
            lon, lat, time, meteogram_type
        )
        return dbc.Col(
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

    def _get_meteogram_image(
            self, lon: float, lat: float, time: str = None,
            meteogram_type: str = 'classical_wave'
    ) -> html.Img:
        params = self._get_params(lon, lat, meteogram_type, time)
        key = ",".join(str(e) for e in list(params.values()))
        if key in self._previous_images:
            return self._previous_images[key]
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
        image = html.Img(src=image_url, style={'padding': '20px'})
        self._previous_images[key] = image
        return image

    @staticmethod
    def _get_params(lon: float, lat: float,
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

    @staticmethod
    def _get_meteogram_selection():
        current_date = datetime.now().date()
        min_date_allowed = current_date - timedelta(days=10)
        max_date_allowed = current_date
        return dbc.Row([
            dbc.Col(
                [
                    dbc.Label("Select Date:", className='mb-2',
                              style={'display': 'block'}),
                    dcc.DatePickerSingle(
                        id=METEOGRAM_DATE_PICKER_ID,
                        min_date_allowed=min_date_allowed,
                        max_date_allowed=max_date_allowed,
                        initial_visible_month=current_date,
                        date=current_date,
                        className="mb-2",
                        style={'width': '230px', 'marginBottom': '20px'}
                    )
                ],
                className='mb-4',  # Add margin-bottom for spacing
            ),
            dbc.Col(
                [
                    dbc.Label("Select Forecast Type:", className='mb-2',
                              style={'display': 'block'}),
                    dcc.Dropdown(
                        id=METEOGRAM_CHOOSER_ID,
                        options=[
                            {'label': 'classical_10d', 'value': 'classical_10d'},
                            {'label': 'classical_15d', 'value': 'classical_15d'},
                            {'label': 'classical_15d_with_climate',
                             'value': 'classical_15d_with_climate'},
                            {'label': 'classical_plume', 'value': 'classical_plume'},
                            {'label': 'classical_wave', 'value': 'classical_wave'}
                        ],
                        value='classical_wave',
                        className="mb-2",
                        style={'width': '400px'}
                    )
                ],
                className='mb-4',  # Add margin-bottom for spacing
            )
        ])

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self._feature_handler = feature_handler

    def register_callbacks(self, app: dash.Dash, component_ids: List[str]):
        lon = self._get_default_tuple()[0]
        lat = self._get_default_tuple()[1]
        label = self._get_default_tuple()[2]

        @app.callback(
            Output(METEOGRAM_IMAGE_ID, 'children'),
            Input("scattermap", 'clickData'),
            Input(METEOGRAM_DATE_PICKER_ID, 'date'),
            Input(METEOGRAM_CHOOSER_ID, 'value')
        )
        def update_meteogram_image(click_data, date_value, forecast_value):
            meteo_lon = click_data['points'][0]['lon'] if click_data else lon
            meteo_lat = click_data['points'][0]['lat'] if click_data else lat
            meteo_label = click_data['points'][0]['text'] if click_data \
                else label
            date_string = date.fromisoformat(date_value). \
                strftime('%Y-%m-%dT00:00:00Z') if date_value else None
            return meteo_label, self._get_meteogram_image(
                meteo_lon, meteo_lat, date_string, forecast_value
            )
