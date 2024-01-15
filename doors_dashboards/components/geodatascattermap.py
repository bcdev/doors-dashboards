import math

from dash import dcc
from dash.development.base_component import Component
import os
import plotly.graph_objs as go
from typing import List
from typing import Tuple

from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.point import Point


def convert_points(points: List[Point]) -> Tuple[List[float], List[float], List[str]]:
    lons = [item[0] for item in points]
    lats = [item[1] for item in points]
    labels = [item[2] for item in points]
    return lons, lats, labels


def get_center(lons: List[float], lats: List[float]) -> Tuple[float, float]:
    center_lon = min(lons) + (max(lons) - min(lons)) / 2
    center_lat = min(lats) + (max(lats) - min(lats)) / 2
    return center_lon, center_lat


def get_zoom_level(lons: List[float], lats: List[float], center_lon: float, center_lat: float) -> float:
    max_distance = max(
        abs(lat - center_lat) + abs(lon - center_lon)
        for lat, lon in zip(lats, lons))
    log = math.log(max_distance, 2)
    zoom_level = math.floor(8 - log)
    return zoom_level


class GeoScatterMapComponent(DashboardComponent):

    def get(self, graph_id: str, points: List[Point], selected_variable: str, **kwargs) -> Component:
        lons, lats, labels = convert_points(points)

        center_lon, center_lat = get_center(lons, lats)

        zoom = get_zoom_level(lons, lats, center_lon, center_lat)

        mapbox_token = os.environ.get("MAPBOX_TOKEN")

        variable_values = []

        if selected_variable == 'temperature [°c]':
            temperature_values = [float(item[2].split('<br>')[4].split(': ')[1]) for item in points]
            variable_values = temperature_values
        elif selected_variable == 'salinity [psu]':
            salinity_values = [float(item[2].split('<br>')[5].split(': ')[1]) for item in points]
            variable_values = salinity_values
        elif selected_variable == 'secchi disk [m]':
            secchi_values = [float(item[2].split('<br>')[6].split(': ')[1]) for item in points]
            variable_values = secchi_values
        else:
            chl_a_values = [float(item[2].split('<br>')[3].split(': ')[1]) for item in points]
            variable_values = chl_a_values

        figure = go.Figure()

        figure.add_trace(go.Scattermapbox(
            lat=lats, lon=lons, mode='markers',
            marker=go.scattermapbox.Marker(
                size=9,
                color=variable_values,
                colorscale='Viridis',
                colorbar=dict(title=selected_variable)
            ),
            text=labels
        ))

        mapbox = dict(
            zoom=zoom,
            accesstoken=mapbox_token,
            center=dict(lat=center_lat, lon=center_lon),
        )
        figure.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            mapbox_style='open-street-map'
        )
        figure.update_layout(mapbox=mapbox)

        return dcc.Graph(
            id=graph_id,
            figure=figure,
            style={
                'width': '100%',
                'height': '100%'
            },
        )
