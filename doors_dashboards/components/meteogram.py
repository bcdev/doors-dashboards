from dash import dcc, no_update, callback
from dash import html
from dash import dash
from dash import Input
from dash import State
from dash import Output
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

from doors_dashboards.components.constant import METEOGRAM_TYPE_TEMPLATE, FONT_COLOR, \
    FONT_SIZE, FONT_FAMILY, PLOT_BGCOLOR, FONT_SIZE_NUMBER, GENERAL_STORE_ID
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

BASE_PARAMS = {
    "format": "png"
}
COMPONENT_STORE_ID = "meteogram_component_store"
HEADERS = {"accept": "application/json"}
METEOGRAM_ENDPOINT = \
    "https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram/"
METEOGRAM_IMAGE_ID = "meteogram_image"
METEOGRAM_DATE_PICKER_ID = "meteogram_date_picker"
METEOGRAM_CHOOSER_ID = "meteogram_chooser"
METEOGRAM_TYPES = [
    {'label': 'Classical 10d', 'value': 'classical_10d'},
    {'label': 'Classical 15d', 'value': 'classical_15d'},
    {'label': 'Classical 15d with climate',
     'value': 'classical_15d_with_climate'},
    {'label': 'Classical plume', 'value': 'classical_plume'},
    {'label': 'Classical wave', 'value': 'classical_wave'}

]
METEOGRAM_TYPE_TO_ID = {meteogram["label"]: METEOGRAM_TYPE_TEMPLATE.format(meteogram[
                                                                               "value"])
                        for
                        meteogram in METEOGRAM_TYPES}
TEMP_STORE_ID = "meteogram_temp_store"


class MeteogramComponent(DashboardComponent):
    def __init__(self, dashboard_id: str = None):
        self._default_tuple = None
        self._feature_handler = None
        self._meteogram_image = None
        self._previous_images = dict()
        self._dashboard_id = dashboard_id

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
        return html.Div(
            children=[
                dcc.Store(id=COMPONENT_STORE_ID, storage_type='session'),
                dcc.Store(id=TEMP_STORE_ID, storage_type='session'),
                dbc.Col(
                    dcc.Loading(
                        id="loading-meteogram",
                        children=[meteogram_image],
                        type="circle",
                    ),
                    style={
                        'color': FONT_COLOR,
                        'fontSize': FONT_SIZE,
                        'fontFamily': FONT_FAMILY,
                        'backgroundColor': PLOT_BGCOLOR,
                        'flex': '1',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'height': '80vh',
                        'width': '100%'
                    },
                    id=sub_component_id,
                    className="p-4 text-center font-weight-bold"
                )
            ]
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
            return dbc.Label(
                f'Meteogram could not be loaded: {response.reason}',
                style={'fontFamily': FONT_FAMILY, 'color': FONT_COLOR,
                       'fontSize': FONT_SIZE_NUMBER}
            )
        response_data = response.json()
        image_url = response_data.get('data', {}).get('link', {}).get('href')
        if not image_url:
            return dbc.Label('Meteogram could not be loaded: '
                             'No image url in response from ECMWF',
                             style={'fontFamily': FONT_FAMILY, 'color': FONT_COLOR,
                                    'fontSize': FONT_SIZE_NUMBER})
        image = html.Img(src=image_url, style={'padding': '20px', 'maxWidth': '100%',
                                               'width': '100%', 'height': '70vh'
                                               },
                         className="col-lg-6")
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
        default_value = METEOGRAM_TYPES[0]['label']
        return html.Div([
            html.Div("Date", className="col-auto px-1 m-2", style={
                "color": FONT_COLOR, "fontFamily": FONT_FAMILY}),
            html.Div(dcc.DatePickerSingle(
                id=METEOGRAM_DATE_PICKER_ID,
                min_date_allowed=min_date_allowed,
                max_date_allowed=max_date_allowed,
                initial_visible_month=current_date,
                date=current_date,
                day_size=50,
                style={'fontFamily': FONT_FAMILY},
            ), className="col-auto px-1"),
            html.Div("Forecast Type", className="col-auto px-1 m-2", style={
                "color": FONT_COLOR, "fontFamily": FONT_FAMILY}),
            html.Div(dbc.DropdownMenu(
                id=METEOGRAM_CHOOSER_ID,
                label=default_value,
                children=[
                    dbc.DropdownMenuItem(
                        meteogram_type, id=meteogram_type_id, n_clicks=1,
                        style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY})
                    for meteogram_type, meteogram_type_id in
                    METEOGRAM_TYPE_TO_ID.items()
                ],
                style={'fontFamily': FONT_FAMILY,
                       'color': FONT_COLOR, 'fontSize': FONT_SIZE},
                color="secondary",
            ), className="col-auto px-1"),
        ], className="row justify-content-start m-1")

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self._feature_handler = feature_handler

    def register_callbacks(self, component_ids: List[str], dashboard_id: str):
        lon = self._get_default_tuple()[0]
        lat = self._get_default_tuple()[1]
        label = self._get_default_tuple()[2]

        @callback(
            Output(METEOGRAM_IMAGE_ID, 'children'),
            Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            Input(COMPONENT_STORE_ID, "data"),
            State(COMPONENT_STORE_ID, "data"),
        )
        def update_meteogram_image(general_data, component_data, component_state_data):
            if general_data is not None:
                meteogram_data = general_data.get("selected_data")
                meteo_lon = meteogram_data.get('lon') if meteogram_data else lon
                meteo_lat = meteogram_data.get('lat') if meteogram_data else lat
                meteo_label = meteogram_data.get('label') if meteogram_data else label
            else:
                meteo_lon = lon
                meteo_lat = lat
                meteo_label = label
            if component_state_data is not None:
                if component_data is not None:
                    component_data.update(component_state_data)
                else:
                    component_data = component_state_data
                date_string = component_data.get("date", "") if component_data.get(
                    "date") else None
                forecast_value = component_data.get("meteogram_type_value",
                                                    METEOGRAM_TYPES[0]["value"])
            else:
                date_string = None
                forecast_value = METEOGRAM_TYPES[0]["value"]

            return dcc.Loading(
                id="loading-meteogram",
                children=[meteo_label, self._get_meteogram_image(meteo_lon, meteo_lat,
                                                                 date_string,
                                                                 forecast_value)],
                type="default"
            )

        @callback(
            Output(TEMP_STORE_ID, "data", allow_duplicate=True),
            [Input(dropdown_id, 'n_clicks_timestamp')
             for dropdown_id in list(METEOGRAM_TYPE_TO_ID.values())],
            prevent_initial_call=True
        )
        def selector_to_temp_store(*timestamps):
            clicked_index = timestamps.index(
                max(t for t in timestamps if t is not None))
            meteogram_drp_option_value = METEOGRAM_TYPES[clicked_index]['value']
            meteogram_drp_option_label = METEOGRAM_TYPES[clicked_index]['label']
            temp_data = {
                'meteogram_type_value': meteogram_drp_option_value,
                'meteogram_type_label': meteogram_drp_option_label
            }

            return temp_data

        @callback(
            Output(METEOGRAM_CHOOSER_ID, "label"),
            Input(COMPONENT_STORE_ID, "data"),
            prevent_initial_call=True
        )
        def component_store_to_drp_label(component_data):
            if component_data is None:
                return no_update
            selected_label = component_data.get("meteogram_type_label",
                                                METEOGRAM_TYPES[0]["label"])
            return selected_label

        @callback(
            Output(COMPONENT_STORE_ID, "data",
                   allow_duplicate=True),
            Input(METEOGRAM_DATE_PICKER_ID, 'date'),
            State(COMPONENT_STORE_ID, "data"),
            prevent_initial_call=True
        )
        def datepicker_to_component_store(date_value, component_data):
            if component_data is not None:
                component_data = component_data or {}
            date_string = date.fromisoformat(date_value). \
                strftime('%Y-%m-%dT00:00:00Z') if date_value else None
            selected_date = {
                'date': date_string
            }
            component_data.update(selected_date)
            return component_data

        @callback(
            Output(COMPONENT_STORE_ID, "data", allow_duplicate=True),
            Input(TEMP_STORE_ID, 'data'),
            State(COMPONENT_STORE_ID, "data"),
            prevent_initial_call=True
        )
        def temp_to_component_store(temp_data, component_data):
            if temp_data is None:
                return no_update
            component_data = component_data or {}
            component_data.update(temp_data)
            return component_data
