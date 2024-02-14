from typing import Dict, List
from dash import Dash, Input, Output, dash
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
                self.feature_handler.select_collection(selected_collection)
                return selected_collection
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
        return dbc.Col([
            dbc.Label('Collection', className='col-',
                      style={'fontSize': '25px', 'float': 'left', 'fontFamily':
                          FONT_FAMILY, 'color': FONT_COLOR,
                             'padding': '29px 20px 0px 40px'}),
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
        ],
            width=4,
            className='mb-4',
            style={'margin': '23px 0 0 -19px'}
        )
