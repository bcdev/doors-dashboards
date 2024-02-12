from dash import Dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash.development.base_component import Component
import math
import os
import plotly.graph_objs as go
from typing import Dict
from typing import List
from typing import Tuple

from doors_dashboards.components.constant import PLOT_BGCOLOR, FONT_FAMILY
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler


def get_center(lons: List[float], lats: List[float]) -> Tuple[float, float]:
    center_lon = min(lons) + (max(lons) - min(lons)) / 2
    center_lat = min(lats) + (max(lats) - min(lats)) / 2
    return center_lon, center_lat


def get_zoom_level(lons: List[float], lats: List[float],
                   center_lon: float, center_lat: float) -> float:
    max_distance = max(
        abs(lat - center_lat) + abs(lon - center_lon)
        for lat, lon in zip(lats, lons)
    )
    log = math.log(max_distance, 2)
    zoom_level = math.floor(8 - log)
    return zoom_level


class ScatterMapComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None

    def get(self, sub_component: str, sub_component_id: str, sub_config: Dict) -> Component:
        points = sub_config.get("points")
        marker_size = sub_config.get("marker_size", 10)
        marker_color = sub_config.get("marker_color", "blue")
        mapbox_style = sub_config.get("mapbox_style", "open-street-map")
        selected_variable = sub_config.get("selected_variable", "")

        figure = go.Figure()

        all_lons = []
        all_lats = []
        all_labels = []

        for collection in self.feature_handler.get_collections():

            lons, lats, labels = self.feature_handler.get_points_as_tuples(
                collection
            )
            all_lons.extend(lons)
            all_lats.extend(lats)
            all_labels.extend(labels)

            if selected_variable:
                variable_values = [
                    point[3].get(selected_variable) for point in points
                ]

            figure.add_trace(go.Scattermapbox(
                lat=lats, lon=lons, mode='markers',
                marker=go.scattermapbox.Marker(
                    size=marker_size, color=marker_color
                ),
                text=labels,
                showlegend=False
            ))

        center_lon, center_lat = get_center(all_lons, all_lats)

        zoom = get_zoom_level(all_lons, all_lats, center_lon, center_lat)

        mapbox_token = os.environ.get("MAPBOX_TOKEN")

        mapbox = dict(
            zoom=zoom,
            accesstoken=mapbox_token,
            center=dict(lat=center_lat, lon=center_lon),
        )
        figure.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            mapbox_style=mapbox_style,
            hoverlabel=dict(
                bgcolor="#7D8FA9",
                font_color="white",
                font_family=FONT_FAMILY
            ),
        )
        figure.update_layout(mapbox=mapbox)
        figure.update_layout()
        scattermap_graph = dcc.Graph(
            id=sub_component_id,
            figure=figure,
            style={
                'width': '100%',
                'height': '80vh',
            },
        )
        return dbc.Col(
            scattermap_graph,
            style={
                'flex': '1',
                'margin': '2px',
                'alignItems': 'center',
                'backgroundColor': PLOT_BGCOLOR,
                'padding': '15px',
                'border-radius': '15px'
            }
        )

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def register_callbacks(self, app: Dash, component_ids: Dict[str, str]):
        pass
