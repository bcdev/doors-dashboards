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


def get_zoom_level(
        lons: List[float], lats: List[float], center_lon: float, center_lat: float
) -> float:
    max_distance = max(
        abs(lat - center_lat) + abs(lon - center_lon)
        for lat, lon in zip(lats, lons)
    ) * 6
    return 8 + max_distance


class ScatterMapComponent(DashboardComponent):

    def get(self,
            graph_id: str,
            points: List[Point],
            marker_size: int = 9,
            marker_color: str = 'blue',
            mapbox_style: str = 'open-street-map',
            **kwargs) -> Component:
        lons, lats, labels = convert_points(points)

        center_lon, center_lat = get_center(lons, lats)

        zoom = get_zoom_level(lons, lats, center_lon, center_lat)

        mapbox_token = os.environ.get("MAPBOX_TOKEN")

        figure = go.Figure(
            go.Scattermapbox(
                lat=lats, lon=lons, mode='markers',
                marker=go.scattermapbox.Marker(
                    size=marker_size, color=marker_color
                ),
                text=labels
            )
        )
        mapbox = dict(
            zoom=zoom,
            accesstoken=mapbox_token,
            center=dict(lat=center_lat, lon=center_lon),
        )
        figure.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(x=0.01, y=0.05, traceorder="normal"),
            mapbox_style=mapbox_style
        )
        figure.update_layout(mapbox=mapbox)

        return dcc.Graph(
            id=graph_id,
            figure=figure,
            style={'height': '1000px'}
        )
