from dash import Dash, Output, Input, State, no_update
from dash import dcc
import dash_bootstrap_components as dbc
from dash.development.base_component import Component
import math
import os
import plotly.graph_objs as go
from typing import Dict
from typing import List
from typing import Tuple
from shapely.geometry import Point

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

    def get(self, sub_component: str, sub_component_id: str,
            sub_config: Dict) -> Component:
        points = sub_config.get("points")
        marker_size = sub_config.get("marker_size", 10)
        marker_color = sub_config.get("marker_color", "blue")
        mapbox_style = sub_config.get("mapbox_style", "carto-positron")
        selected_variable = sub_config.get("selected_variable", "")

        figure = go.Figure()

        all_lons = []
        all_lats = []

        for collection in self.feature_handler.get_collections():

            lons, lats, labels, variable_values, custom_data = (
                self.feature_handler.get_points_as_tuples(collection))
            all_lons.extend(lons)
            all_lats.extend(lats)
            if variable_values:
                color_code_config = self.feature_handler.get_color_code_config(
                    collection
                )
                marker = go.scattermapbox.Marker(
                    size=marker_size,
                    color=variable_values,
                    colorscale=color_code_config.get("color_range", "Viridis"),
                    colorbar=dict(title=color_code_config.get("name")),
                    cmin=color_code_config.get("color_min_value"),
                    cmax=color_code_config.get("color_max_value")
                )
            else:
                marker_color = self.feature_handler.get_color(collection)
                marker = go.scattermapbox.Marker(
                    size=marker_size,
                    color=marker_color
                )

            figure.add_trace(go.Scattermapbox(
                lat=lats, lon=lons, mode='markers',
                marker=marker,
                text=labels,
                name=collection,
                customdata=custom_data,
                selected=go.scattermapbox.Selected(marker={"color": "yellow",
                                                           "size": 25}
                                                   )
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
            clickmode='event+select',
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
        scattermap_graph = dcc.Graph(
            id=sub_component_id,
            figure=figure,
            style={
                'width': '100%',
                'height': '95vh',
            },
        )
        figure.update_layout(
            legend=dict(
                x=0,
                y=1,
                traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=12,
                    color="black"
                ),
            )
        )
        return dbc.Col(
            scattermap_graph,
            style={
                'flex': '1',
                'margin': '2px',
                'alignItems': 'center',
                'backgroundColor': PLOT_BGCOLOR, 'padding': '40px',
                'border-radius': '15px',
                'margin-right': '5px'
            }
        )

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def register_callbacks(self, app: Dash, component_ids: Dict[str, str]):
        @app.callback(
            Output("general", "data"),
            Input("scattermap", 'clickData'),
        )
        def update_general_store_after_station_selection(
                click_data
        ):
            if click_data is None:
                return no_update
            general_data = {}
            collection_name = click_data['points'][0]['customdata']
            if "collection" not in general_data:
                general_data["collection"] = (
                    collection_name)
            if "groups" not in general_data:
                group_name = self.feature_handler.get_levels(collection_name)
                lon = click_data['points'][0]['lon']
                lat = click_data['points'][0]['lat']
                p = Point(lon, lat)
                gdf = self.feature_handler.get_df(collection_name)
                gdf = gdf[gdf["geometry"].geom_equals(p)]
                if len(gdf) > 0:
                    group = gdf.iloc[0][group_name]
                    general_data["groups"] = {}
                    general_data["groups"][collection_name] = (
                     group)
            if "variable" not in general_data:
                general_data["variable"] = {}
            general_data["variable"][collection_name] = (
                self.feature_handler.get_default_variable(collection_name))
            return general_data

