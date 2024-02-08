from typing import Dict, List
from dash import dcc, html, Dash, Input, Output, dash
import dash_bootstrap_components as dbc
from dash.development.base_component import Component

from doors_dashboards.components.constant import SELECT_CRUISE_DRP, FONT_FAMILY, \
    FONT_COLOR, SELECT_STATION_DRP
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

SELECT_COLLECTION_DRP = 'collection-drp'


class SelectCollectionComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None

    def register_callbacks(self, app: Dash, component_ids: List[str]):
        collections = self.feature_handler.get_collections()
        dropdown_ids = [f'collection_drp_option_{i}' for i in range(len(collections))]

        @app.callback(
            [Output(SELECT_CRUISE_DRP, 'children'),
             Output(SELECT_CRUISE_DRP, 'label'),
             Output(SELECT_STATION_DRP, 'children',allow_duplicate=True),
             Output(SELECT_STATION_DRP, 'label', allow_duplicate=True)],
            [Input(dropdown_id, 'n_clicks_timestamp') for dropdown_id in dropdown_ids],
            prevent_initial_call=True
        )
        def update_selected_cruise_drp(*timestamps):
            if any(timestamps):
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                selected_collection = collections[latest_timestamp_index]
                self.feature_handler.select_collection(selected_collection)
                nested_level_values = self.feature_handler.get_nested_level_values(
                    selected_collection)
                cruises = list(nested_level_values.keys())

                cruise_dropdown_items = [
                    dbc.DropdownMenuItem(cruise,
                                         id=f'cruise_drp_option_{i}',
                                         n_clicks=1) for i, cruise in enumerate(cruises)
                ]
                stations = list(nested_level_values.get(cruises[0]).keys())
                stations.sort()
                station_dropdown_items = [
                    dbc.DropdownMenuItem(station,
                                         id=f'station_drp_option_{i}',
                                         n_clicks=1) for i, station in enumerate(
                        stations)
                ]
                return (cruise_dropdown_items, cruises[0] if cruises else None,
                        station_dropdown_items, stations[0] if stations else None)
            else:
                return dash.no_update

        @app.callback(
            Output(SELECT_COLLECTION_DRP, 'label'),
            # Update the label of the dropdown menu
            [Input(dropdown_id, 'n_clicks_timestamp') for dropdown_id in dropdown_ids]
        )
        def update_label(*timestamps):
            if any(timestamps):
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                selected_collection = collections[latest_timestamp_index]
                return selected_collection
            else:
                return dash.no_update

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def get(self, sub_component: str, sub_component_id_str,
            sub_config: Dict) -> Component:
        collections = self.feature_handler.get_collections()
        default_value = self.feature_handler.get_collections()[0]
        return dbc.Col([
            dbc.DropdownMenu(
                id=SELECT_COLLECTION_DRP,
                label=default_value,
                children=[
                    dbc.DropdownMenuItem(collection,
                                         id=f'collection_drp_option_{i}',
                                         n_clicks=1) for i, collection in
                    enumerate(collections)
                ],
                style={'fontSize': 'x-large', 'fontFamily': FONT_FAMILY,
                       'color': FONT_COLOR, 'width': '500px'},
                className="m-4",
                color="secondary"
            )
        ],
            width=4,
            className='mb-4',
            style={'margin': '25px 0 0 54px'}
        )
