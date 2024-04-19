from dash import Dash
from dash import Input
from dash import no_update
from dash import Output
from dash import State
from dash import dcc
import dash_bootstrap_components as dbc
from dash.development.base_component import Component
import math
import os
import random
import plotly.graph_objs as go
from typing import Dict
from typing import List
from typing import Tuple
from shapely.geometry import Point

from doors_dashboards.components.constant import FONT_FAMILY, GENERAL_STORE_ID
from doors_dashboards.components.constant import GROUP
from doors_dashboards.components.constant import GROUPS_SECTION
from doors_dashboards.components.constant import MAIN_GROUP
from doors_dashboards.components.constant import PLOT_BGCOLOR
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

    def __init__(self, dashboard_id: str = None):
        self.feature_handler = None
        self._dashboard_id = dashboard_id

    def get(self, sub_component: str, sub_component_id: str,
            sub_config: Dict) -> Component:
        points = sub_config.get("points")
        marker_size = sub_config.get("marker_size", 10)
        mapbox_style = sub_config.get("mapbox_style", "carto-positron")
        selected_variable = sub_config.get("selected_variable", "")

        figure = go.Figure()

        all_lons = []
        all_lats = []

        colors = [
            "blue", "red", "green", "yellow", "orange",
            "purple", "cyan", "magenta", "lime",
            "teal", "brown", "navy"
        ]

        for collection in self.feature_handler.get_collections():
            lons, lats, labels, variable_values = (
                self.feature_handler.get_points_as_tuples(collection)
            )
            customdata = [collection] * len(lons)
            all_lons.extend(lons)
            all_lats.extend(lats)

            color_index = random.randint(0, len(colors) - 1)

            if variable_values:
                color_code_config = self.feature_handler.get_color_code_config(
                    collection)
                marker = go.scattermapbox.Marker(
                    size=marker_size,
                    color=variable_values,
                    colorscale=color_code_config.get("color_range", "Viridis"),
                    colorbar=dict(title=color_code_config.get("name")),
                    cmin=color_code_config.get("color_min_value"),
                    cmax=color_code_config.get("color_max_value")
                )
            else:
                marker = go.scattermapbox.Marker(
                    size=marker_size,
                    color=colors[color_index]
                )
                del colors[color_index]

            map_mode_config = self.feature_handler.get_map_mode_config(collection)
            if map_mode_config != '':
                config_dict = eval(map_mode_config.replace("'", '"'))
                mode = config_dict.get("mode", "")
            else:
                mode = 'markers'

            figure.add_trace(go.Scattermapbox(
                lat=lats, lon=lons, mode=mode,
                marker=marker,
                text=labels,
                name=collection,
                customdata=customdata,
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

        figure.update_layout(mapbox=mapbox)

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
                'padding': '20px',
                'borderRadius': '15px',
                'marginRight': '5px',
                'height': '100%'
            },
        )

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def register_callbacks(self, app: Dash, component_ids: Dict[str, str],
                           dashboard_id: str):
        @app.callback(
            Output(f"{dashboard_id}-general", "data", allow_duplicate=True),
            Input("scattermap", 'clickData'),
            State(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            prevent_initial_call=True
        )
        def update_general_store_after_point_selection(click_data, general_data):
            if click_data is None:
                return no_update
            general_data = general_data or {}
            collection_name = click_data['points'][0]['customdata']
            general_data["collection"] = collection_name
            if GROUPS_SECTION not in general_data:
                general_data[GROUPS_SECTION] = {}
            lon = click_data['points'][0]['lon']
            lat = click_data['points'][0]['lat']
            p = Point(lon, lat)
            gdf = self.feature_handler.get_df(collection_name)
            gdf = gdf[gdf["geometry"].geom_equals(p)]
            levels = self.feature_handler.get_levels(collection_name)
            text = click_data['points'][0]['text']
            general_data["selected_data"] = {
                'lon': lon,
                'lat': lat,
                'label': text
            }
            if len(levels) > 0:
                if len(levels) == 3:
                    series = gdf.iloc[0][[levels[0], levels[1]]]
                    general_data[GROUPS_SECTION][collection_name] = {
                        MAIN_GROUP: series[levels[0]],
                        GROUP: series[levels[1]]
                    }
                else:
                    series = gdf.iloc[0][[levels[0]]]
                    general_data[GROUPS_SECTION][collection_name] = {
                        GROUP: series[levels[0]]
                    }
            return general_data

        @app.callback(
            Output("scattermap", 'figure', allow_duplicate=True),
            [Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data")],
            State('scattermap', 'figure'),
            prevent_initial_call=True
        )
        def update_selected_dropdown_point_on_scattermap(general_data, current_figure):
            if "collection" in general_data:
                collection_name = general_data["collection"]
                levels = self.feature_handler.get_levels(collection_name)
                if len(levels) == 1 and levels[0] != "station":
                    if isinstance(current_figure, dict) and "data" in current_figure:
                        current_figure = go.Figure(current_figure)
                        current_figure['data'] = [trace for trace in
                                                  current_figure['data'] if
                                                  trace['name'] != "Selected Station"]
                        return current_figure

            if "groups" in general_data:
                group_value = general_data.get("groups", {}). \
                    get(general_data["collection"])
                if isinstance(group_value, dict) and 'group' in group_value:
                    group_value = group_value['group']
            else:
                collection_name = general_data.get("collection", {})
                group_values = self.feature_handler.get_nested_level_values(
                    collection_name)
                if isinstance(group_values, dict):
                    default_key = list(group_values.keys())[0]
                    group_value = default_key
                else:
                    group_values.sort()
                    group_value = group_values[0] if len(
                        group_values) > 1 else group_values
            df = self.feature_handler.get_df(general_data.get("collection", {}))
            geometry = df[df["station"] == group_value]["geometry"]
            if geometry.empty:
                return no_update
            lon, lat = geometry.x.values, geometry.y.values
            highlighted_trace = go.Scattermapbox(
                lat=lat,
                lon=lon,
                mode='markers',
                marker=dict(
                    size=15,
                    color="#5C050B",
                ),
                name="Selected Station",
                text=group_value
            )

            if isinstance(current_figure, dict) and "data" in current_figure:
                current_figure['data'] = [trace for trace in current_figure['data'] if
                                          trace['name'] != "Selected Station"]
                current_figure = go.Figure(current_figure)
                current_figure.add_trace(highlighted_trace)
                return current_figure
