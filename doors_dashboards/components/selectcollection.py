from dash import callback
from dash import dash
from dash import html
from dash import Input
from dash import no_update
from dash import Output
from dash import State
from dash.development.base_component import Component
import dash_bootstrap_components as dbc
from typing import Dict
from typing import List

from doors_dashboards.components.constant import (
    COLLECTION,
    GENERAL_STORE_ID,
    COLLECTION_TEMPLATE,
    FONT_FAMILY,
    FONT_COLOR,
)
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

SELECT_COLLECTION_DRP = "collection-drp"

COLLECTION_TO_ID = {}


class SelectCollectionComponent(DashboardComponent):

    def __init__(self, dashboard_id: str = None):
        self.feature_handler = None
        self.collection_to_id = {}
        self._dashboard_id = dashboard_id

    def register_callbacks(self, component_ids: List[str], dashboard_id: str = None):

        @callback(
            Output(f"{dashboard_id}-{SELECT_COLLECTION_DRP}", "label"),
            # Update the label of the dropdown menu
            [
                Input(dropdown_id, "n_clicks_timestamp")
                for dropdown_id in list(self.collection_to_id.values())
            ],
        )
        def update_label(*timestamps):
            if any(timestamps):
                collections = list(self.collection_to_id.keys())
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None)
                )
                selected_collection = collections[latest_timestamp_index]
                return selected_collection
            else:
                return dash.no_update

        @callback(
            [
                Output(f"{dashboard_id}-general", "data", allow_duplicate=True),
                Output(
                    f"{dashboard_id}-{SELECT_COLLECTION_DRP}",
                    "label",
                    allow_duplicate=True,
                ),
            ],
            Input(f"{dashboard_id}-collection_selector", "data"),
            State(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            prevent_initial_call=True,
        )
        def update_general_store(selected_data, general_data):
            if selected_data is not None:
                general_data = general_data or {}
                general_data[COLLECTION] = selected_data[COLLECTION]
                if "selected_data" in general_data:
                    general_data.pop("selected_data")
            return general_data, selected_data[COLLECTION]

        @callback(
            Output(f"{dashboard_id}-collection_selector", "data"),
            Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
        )
        def update_collection_selector_store_after_general_store_update(general_data):
            if general_data is None:
                return no_update

            collection = general_data[COLLECTION]
            coll = {COLLECTION: collection}
            return coll

        @callback(
            Output(f"{dashboard_id}-collection_selector", "data", allow_duplicate=True),
            [
                Input(dropdown_id, "n_clicks_timestamp")
                for dropdown_id in list(self.collection_to_id.values())
            ],
            prevent_initial_call=True,
        )
        def update_collection_selector_store(*timestamps):
            if any(timestamps):
                collections = list(self.collection_to_id.keys())
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None)
                )
                coll = {COLLECTION: collections[latest_timestamp_index]}
                return coll
            else:
                return dash.no_update

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler
        collections = self.feature_handler.get_collections()
        self.collection_to_id = {c: COLLECTION_TEMPLATE.format(c) for c in collections}

    def get(
        self, sub_component: str, sub_component_id_str, sub_config: Dict
    ) -> Component:
        collections = list(self.collection_to_id.keys())
        default_value = collections[0]
        return html.Div(
            [
                dbc.Label(
                    "Collection",
                    style={
                        "fontSize": "20px",
                        "float": "left",
                        "fontFamily": FONT_FAMILY,
                        "color": FONT_COLOR,
                        "padding": "5px 15px 0 10px",
                    },
                ),
                dbc.DropdownMenu(
                    id=f"{self._dashboard_id}-{SELECT_COLLECTION_DRP}",
                    label=default_value,
                    children=[
                        dbc.DropdownMenuItem(
                            collection,
                            id=collection_id,
                            n_clicks=1,
                            style={"fontSize": "larger", "fontFamily": FONT_FAMILY},
                        )
                        for collection, collection_id in self.collection_to_id.items()
                    ],
                    style={
                        "fontFamily": FONT_FAMILY,
                        "color": FONT_COLOR,
                        "paddingTop": "5px",
                    },
                    color="secondary",
                ),
            ]
        )
