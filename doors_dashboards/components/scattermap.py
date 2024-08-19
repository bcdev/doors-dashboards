from dash import callback, html
from dash import Input
from dash import no_update
from dash import Output
from dash import State
from dash import dcc
from dash.development.base_component import Component
import math
import matplotlib
import numpy as np
import os
from PIL import Image
import plotly.graph_objs as go
import random
import requests
from shapely.geometry import Point
from typing import Dict
from typing import List
from typing import Tuple

# import numpy as np
import base64
import matplotlib.pyplot as plt
import io


from doors_dashboards.components.constant import (
    COLLECTION,
    FONT_FAMILY,
    PLOT_BGCOLOR,
    GENERAL_STORE_ID,
    GROUPS_SECTION,
    MAIN_GROUP,
    GROUP,
)
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

DEFAULT_COLOR_RANGE = "viridis"
DEFAULT_SELECTION_COLOR = "#CC0000"
SELECTION_COLOR = DEFAULT_SELECTION_COLOR
DEFAULT_SELECTION_SIZE = 17
HEADERS = {"accept": "application/json"}
SELECTION_COLOR = DEFAULT_SELECTION_COLOR
SELECTION_SIZE = DEFAULT_SELECTION_SIZE

TILE_VALUE_SETS = {
    1: {
        "lat_start_index": 0,
        "lat_end_index": 0,
        "lon_start_index": 2,
        "lon_end_index": 2,
        "resolution": 90,
    },
    2: {
        "lat_start_index": 0,
        "lat_end_index": 1,
        "lon_start_index": 4,
        "lon_end_index": 4,
        "resolution": 45,
    },
    3: {
        "lat_start_index": 1,
        "lat_end_index": 2,
        "lon_start_index": 9,
        "lon_end_index": 9,
        "resolution": 22.5,
    },
    4: {
        "lat_start_index": 3,
        "lat_end_index": 4,
        "lon_start_index": 18,
        "lon_end_index": 19,
        "resolution": 11.25,
    },
    5: {
        "lat_start_index": 7,
        "lat_end_index": 8,
        "lon_start_index": 36,
        "lon_end_index": 39,
        "resolution": 5.625,
    },
    6: {
        "lat_start_index": 15,
        "lat_end_index": 17,
        "lon_start_index": 73,
        "lon_end_index": 78,
        "resolution": 2.8125,
    },
    7: {
        "lat_start_index": 30,
        "lat_end_index": 34,
        "lon_start_index": 147,
        "lon_end_index": 157,
        "resolution": 1.40625,
    },
}
TILE_ZOOM_LEVEL = 6

XCUBE_COLOR_BAR_URL = "https://doors.api.brockmann-consult.de/api/colorbars"


def get_color_bars():
    response = requests.get(XCUBE_COLOR_BAR_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()


XCUBE_COLOR_BARS = get_color_bars()


def get_color_map_image_stream(var_name: str):
    bd = BACKGROUND_DEFINITONS.get(var_name)
    cm_name = bd.get("colormap")
    for color_bar_group in XCUBE_COLOR_BARS:
        for color_bar in color_bar_group[2]:
            if color_bar[0] == cm_name:
                cbar_png_str = color_bar[1]
                cbar_png_bytes = base64.b64decode(cbar_png_str)
                stream = io.BytesIO(cbar_png_bytes)
                return stream

XCUBE_SERVER_BASE_TILE_URL = "https://doors.api.brockmann-consult.de/api/tiles/{0}/{1}/{2}/{3}/{4}?vmin={5}&vmax={6}&cbar={7}&time={8}"
XCUBE_SERVER_BASE_TIME_URL = "https://doors.api.brockmann-consult.de/api/datasets/{0}/coords/time"

BACKGROUND_DEFINITONS = {
    "chlorophyll": {
        "vmin": 0,
        "vmax": 40,
        "colormap": "chl_DeM2",
        "dataset_name": "cmems-chl-bs",
        "variable_name": "CHL",
        "title": "CHL [milligram m^-3]"
    },
    "salinity": {
        "vmin": 10,
        "vmax": 20,
        "colormap": "haline",
        "dataset_name": "cmcc-sal-bs",
        "variable_name": "so",
        "title": "Salinity [PSU]"
    },
    "sst": {
        "vmin": 280,
        "vmax": 302,
        "colormap": "thermal",
        "dataset_name": "cmems-sst-bs",
        "variable_name": "analysed_sst",
        "title": "Analysed SST [Kelvin]"
    },
}


def get_time_coords(var_name: str) -> List[str]:
    bd = BACKGROUND_DEFINITONS.get(var_name)
    time_url = XCUBE_SERVER_BASE_TIME_URL.format(bd["dataset_name"])
    response = requests.get(time_url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("coordinates")


def get_last_time_coord(var_name: str) -> List[str]:
    return get_time_coords(var_name)[-1]


def get_background_image_layers(var_name: str) -> List[Dict]:
    bd = BACKGROUND_DEFINITONS.get(var_name)
    image_layers = []
    tvs = TILE_VALUE_SETS.get(TILE_ZOOM_LEVEL)
    time = get_last_time_coord(var_name)
    for lat_index in range(tvs["lat_start_index"], tvs["lat_end_index"] + 1):
        lat_0 = 90 - (lat_index * tvs["resolution"])
        lat_1 = lat_0 - tvs["resolution"]
        for lon_index in range(tvs["lon_start_index"], tvs["lon_end_index"] + 1):
            lon_0 = -180 + (lon_index * tvs["resolution"])
            lon_1 = lon_0 + tvs["resolution"]
            # time = "2024-06-29T00%3A00%3A00Z"
            img = XCUBE_SERVER_BASE_TILE_URL.format(
                bd["dataset_name"],
                bd["variable_name"],
                TILE_ZOOM_LEVEL,
                lat_index,
                lon_index,
                bd["vmin"],
                bd["vmax"],
                bd["colormap"],
                time
            )
            coordinates = [
                [lon_0, lat_0],
                [lon_1, lat_0],
                [lon_1, lat_1],
                [lon_0, lat_1],
            ]
            image_layers.append(
                {
                    "below": "traces",
                    "sourcetype": "image",
                    "source": img,
                    "coordinates": coordinates,
                }
            )
    return image_layers


def get_annotations(var_name: str):
    bd = BACKGROUND_DEFINITONS.get(var_name)
    time = get_last_time_coord(var_name)
    annotations = [
        dict(
            x=0.02,
            y=-0.05,
            xref="paper",
            yref="paper",
            text=bd["title"],
            showarrow=False,
            font=dict(size=14),
        ),
        dict(
            x=0.02,
            y=-0.1,
            xref="paper",
            yref="paper",
            text=time,
            showarrow=False,
            font=dict(size=14),
        )
    ]
    vmin = bd["vmin"]
    vmax = bd["vmax"]
    vrange = (vmax - vmin) / 5
    for i in range(6):
        annotations.append(
            dict(
                x=0.2 + (i * 0.15),
                y=-0.075,
                xref="paper",
                yref="paper",
                text=vmin + (i * vrange),
                showarrow=True,
                font=dict(size=12),
            )
        )
    return annotations


def get_center(lons: List[float], lats: List[float], geometry_type: str = "Point") -> (
        Tuple)[float, float]:
    if geometry_type == "Polygon":
        valid_lats = [lat for lat in lats if lat is not None]
        valid_lons = [lon for lon in lons if lon is not None]
        avg_lat = sum(valid_lats) / len(valid_lats) if valid_lats else 0
        avg_lon = sum(valid_lons) / len(valid_lons) if valid_lons else 0
        return avg_lat, avg_lon
    else:
        center_lon = min(lons) + (max(lons) - min(lons)) / 2
        center_lat = min(lats) + (max(lats) - min(lats)) / 2
        return center_lon, center_lat


def get_zoom_level(
        lons: List[float], lats: List[float], center_lon: float, center_lat: float,
        geometry_type: str = "Point"
) -> float:
    if geometry_type == "Polygon":
        valid_coords = [(lat, lon) for lat, lon in zip(lats, lons) if
                        lat is not None and lon is not None]
        max_distance = max(
            abs(lat - center_lat) + abs(lon - center_lon) for lat, lon in valid_coords
        )
        log = math.log(max_distance, 2) if max_distance > 0 else 0
        zoom_level = math.floor(8 - log)
        return zoom_level
    else:
        max_distance = max(
            abs(lat - center_lat) + abs(lon - center_lon) for lat, lon in
            zip(lats, lons)
        )
        log = math.log(max_distance, 2)
        zoom_level = math.floor(8 - log)
        return zoom_level


class ScatterMapComponent(DashboardComponent):

    def __init__(self, dashboard_id: str = None):
        self.feature_handler = None
        self._dashboard_id = dashboard_id

    def get(
        self, sub_component: str, sub_component_id: str, sub_config: Dict
    ) -> Component:
        points = sub_config.get("points")
        marker_size = sub_config.get("marker_size", 10)
        mapbox_style = sub_config.get("mapbox_style", "carto-positron")
        selected_variable = sub_config.get("selected_variable", "")
        background_variable = sub_config.get("background_variable", "")

        figure = go.Figure()

        all_lons = []
        all_lats = []

        for i, collection in enumerate(self.feature_handler.get_collections()):
            geometry_type = self.feature_handler.get_geometry_type(collection)

            if geometry_type == "Point":
                self._process_points(collection, figure, sub_config, all_lons, all_lats)
            else:
                self._process_polygons(collection, figure, sub_config, all_lons,
                                       all_lats)

        # Calculate the center and zoom level after processing all geometries
        center_lon, center_lat = get_center(all_lons, all_lats, geometry_type)
        zoom = get_zoom_level(all_lons, all_lats, center_lon, center_lat, geometry_type)
        mapbox_token = os.environ.get("MAPBOX_TOKEN")
        mapbox_style = sub_config.get("mapbox_style", "carto-positron")

        # Update layout with mapbox configuration
        mapbox = dict(
            zoom=zoom,
            accesstoken=mapbox_token,
            center=dict(lat=center_lat, lon=center_lon),
        )

        figure.update_layout(
            clickmode="event+select",
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            mapbox_style=mapbox_style,
            hoverlabel=dict(
                bgcolor="#7D8FA9", font_color="white", font_family=FONT_FAMILY
            ),
            legend=dict(
                x=0,
                y=1,
                traceorder="normal",
                font=dict(family="sans-serif", size=12, color="black"),
            ),
            mapbox=mapbox,
        )

        # Create the Graph and wrap it in a Div
        scattermap_graph = dcc.Graph(
            id=sub_component_id, figure=figure, style={"height": "81.5vh"}
        )

        return html.Div(
            scattermap_graph,
            style={
                "flex": "1",
                "padding": "20px",
                "alignItems": "center",
                "backgroundColor": PLOT_BGCOLOR,
            },
        )

    def _process_points(
            self, collection, figure, sub_config, all_lons, all_lats
    ):
        marker_size = sub_config.get("marker_size", 10)
        colors = list(matplotlib.colors.CSS4_COLORS.keys())

        lons, lats, labels, variable_values = (
            self.feature_handler.get_points_as_tuples(collection)
        )
        custom_data = [collection] * len(lons)
        all_lons.extend(lons)
        all_lats.extend(lats)

        color_index = random.randint(0, len(colors) - 1)
        color = colors[color_index]
        del colors[color_index]

        if variable_values:
            color_code_config = self.feature_handler.get_color_code_config(collection)
            marker = go.scattermapbox.Marker(
                size=marker_size,
                color=variable_values,
                colorscale=color_code_config.get(
                    "color_range", DEFAULT_COLOR_RANGE
                ),
                colorbar=dict(title=color_code_config.get("name")),
                cmin=color_code_config.get("color_min_value"),
                cmax=color_code_config.get("color_max_value"),
            )
        else:
            marker = go.scattermapbox.Marker(size=marker_size, color=color)
            map_mode_config = self.feature_handler.get_map_mode_config(collection)
            if map_mode_config != "":
                config_dict = eval(map_mode_config.replace("'", '"'))
                mode = config_dict.get("mode", "")
            else:
                mode = "markers"

            figure.add_trace(
                go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode=mode,
                    marker=marker,
                    text=labels,
                    name=collection,
                    customdata=custom_data,
                    selected=go.scattermapbox.Selected(
                        marker={"color": SELECTION_COLOR, "size": SELECTION_SIZE}
                    ),
                )
            )

    def _process_polygons(
            self, collection, figure, sub_config, all_lons, all_lats
    ):
        gdf = self.feature_handler.get_df(collection)
        lons, lats, text = self.feature_handler.get_polygon_data(gdf)
        all_lons.extend(lons)
        all_lats.extend(lats)

        figure.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='lines',
            fill='toself',
            fillcolor='rgba(0, 150, 255, 0.3)',
            line=dict(width=2, color='blue'),
            text=text,
            hoverinfo='text'
        ))

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def register_callbacks(self, component_ids: Dict[str, str], dashboard_id: str):
        @callback(
            Output(f"{dashboard_id}-general", "data", allow_duplicate=True),
            Input("scattermap", "clickData"),
            State(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            prevent_initial_call=True,
        )
        def update_general_store_after_point_selection(click_data, general_data):
            if click_data is None:
                return no_update
            collection_name = click_data.get("points", [{}])[0].get("customdata")
            if collection_name is None:
                return no_update
            general_data = general_data or {}
            collection_name = click_data["points"][0]["customdata"]
            general_data[COLLECTION] = collection_name
            if GROUPS_SECTION not in general_data:
                general_data[GROUPS_SECTION] = {}
            lon = click_data["points"][0]["lon"]
            lat = click_data["points"][0]["lat"]
            p = Point(lon, lat)
            gdf = self.feature_handler.get_df(collection_name)
            gdf = gdf[gdf["geometry"].geom_equals(p)]
            levels = self.feature_handler.get_levels(collection_name)
            text = click_data["points"][0]["text"]
            general_data["selected_data"] = {
                "lon": [lon],
                "lat": [lat],
                "label": [text],
            }
            if len(levels) > 0:
                if len(levels) == 3:
                    series = gdf.iloc[0][[levels[0], levels[1]]]
                    general_data[GROUPS_SECTION][collection_name] = {
                        MAIN_GROUP: series[levels[0]],
                        GROUP: series[levels[1]],
                    }
                else:
                    series = gdf.iloc[0][[levels[0]]]
                    general_data[GROUPS_SECTION][collection_name] = {
                        GROUP: series[levels[0]]
                    }
            return general_data

        @callback(
            Output("scattermap", "figure", allow_duplicate=True),
            [Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data")],
            State("scattermap", "figure"),
            prevent_initial_call=True,
        )
        def update_selected_dropdown_point_on_scattermap(general_data, current_figure):
            if COLLECTION not in general_data:
                return no_update

            collection_name = general_data[COLLECTION]
            df = self.feature_handler.get_df(collection_name)
            label = self.feature_handler.get_label(collection_name)
            if label is None:
                if isinstance(current_figure, dict) and "data" in current_figure:
                    current_figure = go.Figure(current_figure)
                    current_figure["data"] = [
                        trace
                        for trace in current_figure["data"]
                        if not trace["name"].startswith("Selected")
                    ]
                    return current_figure

            if "selected_data" in general_data:
                selected_data = general_data.get("selected_data", {})
                lon = selected_data.get("lon")
                lat = selected_data.get("lat")
                text = selected_data.get("label")
            elif label not in df.columns:
                lon, lat, text = None, None, None
            else:
                if "groups" in general_data:
                    group_value = (
                        general_data.get("groups", {})
                        .get(collection_name, {})
                        .get("group")
                    )
                else:
                    group_values = self.feature_handler.get_nested_level_values(
                        collection_name
                    )
                    if isinstance(group_values, dict):
                        default_key = list(group_values.keys())[0]
                        group_value = default_key
                    else:
                        group_values.sort()
                        group_value = (
                            group_values[0] if len(group_values) > 1 else group_values
                        )
                geometry = df[df[label] == group_value]["geometry"]
                geometries = np.array([geometry.x.values, geometry.y.values])
                geometries = np.unique(geometries, axis=1)
                lon = list(geometries[0])
                lat = list(geometries[1])
                text = [group_value] * len(lon)
                general_data["selected_data"] = {"lon": lon, "lat": lat, "label": text}

            if lon is None or lat is None:
                return no_update

            highlighted_trace = go.Scattermapbox(
                lat=lat,
                lon=lon,
                text=text,
                mode="markers",
                marker=dict(
                    size=SELECTION_SIZE,
                    color=SELECTION_COLOR,
                ),
                name=f"Selected {label.title()}",
            )

            if isinstance(current_figure, dict) and "data" in current_figure:
                new_traces = []
                for trace in current_figure["data"]:
                    if not trace["name"].startswith("Selected"):
                        trace["selectedpoints"] = []
                        new_traces.append(trace)
                current_figure["data"] = new_traces
                current_figure = go.Figure(current_figure)
                current_figure.add_trace(highlighted_trace)
                return current_figure
