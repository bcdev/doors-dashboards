from dash import html
from dash.development.base_component import Component
from copy import deepcopy
from datetime import datetime
import requests
from typing import Dict
import base64
from PIL import Image
from io import BytesIO


from doors_dashboards.core.dashboardcomponent import DashboardComponent

METEOGRAM_ENDPOINT = \
    "https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram/"
HEADERS = {"accept": "application/json"}
BASE_PARAMS = {
    "format": "png"
}


class MeteogramComponent(DashboardComponent):

    def get(self, lon: float, lat: float, time: str = None, meteogram_type: str = 'classical_wave',
            **kwargs) -> Component:
        params = self._get_params(lon, lat, meteogram_type, time, **kwargs)
        response = requests.get(METEOGRAM_ENDPOINT, params=params, headers=HEADERS)
        if response.status_code != 200:
            return html.Label(f'Meteogram could not be loaded: {response.reason}')
        response_data = response.json()
        # image_url = response_data.get('data', {}).get('link', {}).get('href')
        # imgresponse = requests.get(image_url)

        image_url = response_data.get('data', {}).get('link', {}).get('href')
        if not image_url:
            return html.Label('Meteogram could not be loaded: '
                              'No image url in reponse from ECMWF')
        return html.Img(src=image_url, style={'padding': '20px'})

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