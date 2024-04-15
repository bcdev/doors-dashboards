from typing import Dict, List
from dash import Dash, dash
from dash import html
from dash import Input
from dash import no_update
from dash import Output
from dash import State
import dash_bootstrap_components as dbc
from dash.development.base_component import Component

from doors_dashboards.components.constant import COLLECTION_TEMPLATE
from doors_dashboards.components.constant import FONT_FAMILY
from doors_dashboards.components.constant import FONT_COLOR
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

SELECT_COLLECTION_DRP = 'collection-drp'

COLLECTION_TO_ID = {}


class SelectCollectionComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None
        self.collection_to_id = {}

    def register_callbacks(self, app: Dash, component_ids: List[str]):

        @app.callback(
            Output(SELECT_COLLECTION_DRP, 'label'),
            # Update the label of the dropdown menu
            [Input(dropdown_id, 'n_clicks_timestamp')
             for dropdown_id in list(self.collection_to_id.values())]
        )
        def update_label(*timestamps):
            if any(timestamps):
                collections = list(self.collection_to_id.keys())
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                selected_collection = collections[latest_timestamp_index]
                return selected_collection
            else:
                return dash.no_update

        @app.callback(
            [Output("general", "data",
                    allow_duplicate=True),
             Output(SELECT_COLLECTION_DRP, 'label', allow_duplicate=True)],
            Input("collection_selector", 'data'),
            State("general", "data"),
            prevent_initial_call=True
        )
        def update_general_store(selected_data, general_data):
            if selected_data is not None:
                general_data = general_data or {}
                general_data['collection'] = selected_data["collection"]
            return general_data, selected_data["collection"]

        @app.callback(
            Output("collection_selector", "data"),
            Input("general", "data")
        )
        def update_collection_selector_store_after_general_store_update(general_data):
            if general_data is None:
                return no_update

            collection = general_data["collection"]
            coll = {
                    "collection": collection
            }
            return coll

        @app.callback(
            Output("collection_selector", 'data', allow_duplicate=True),
            [Input(dropdown_id, 'n_clicks_timestamp')
             for dropdown_id in list(self.collection_to_id.values())],
            prevent_initial_call=True
        )
        def update_collection_selector_store(*timestamps):
            if any(timestamps):
                collections = list(self.collection_to_id.keys())
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                coll = {
                    "collection": collections[latest_timestamp_index]
                }
                return coll
            else:
                return dash.no_update

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler
        collections = self.feature_handler.get_collections()
        self.collection_to_id = {c: COLLECTION_TEMPLATE.format(c) for c in collections}

    def get(self, sub_component: str, sub_component_id_str,
            sub_config: Dict) -> Component:
        collections = list(self.collection_to_id.keys())
        default_value = collections[0]
        return html.Div(
        [
            dbc.Label('Collection', className='col-',
                      style={'fontSize': '25px', 'float': 'left', 'fontFamily':
                          FONT_FAMILY, 'color': FONT_COLOR,
                             'padding': '5px 20px 0px 462px'}),
            dbc.DropdownMenu(
                id=SELECT_COLLECTION_DRP,
                label=default_value,
                children=[
                    dbc.DropdownMenuItem(
                        collection, id=collection_id, n_clicks=1, style={'fontSize':
                                                                             'larger',
                                                                         'fontfamily': FONT_FAMILY})
                    for collection, collection_id in self.collection_to_id.items()
                ],
                style={'fontFamily': FONT_FAMILY,
                       'color': FONT_COLOR, 'width': '1000px'},
                className="m-4",
                color="secondary",
                size="lg"
            )
        ]
    )
