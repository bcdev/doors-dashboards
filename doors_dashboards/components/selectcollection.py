from typing import Dict, List
from dash import dcc, html, Dash, Input, Output, dash
import plotly.express as px
from dash.development.base_component import Component
from dash_material_ui import FormLabel

from doors_dashboards.components.constant import SELECT_CRUISE_DRP, SELECT_STATION_DRP
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

SELECT_COLLECTION_DRP = 'collection-drp'


class SelectCollectionComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None

    def register_callbacks(self, app: Dash, component_ids: List[str]):
        @app.callback(
            [Output(SELECT_CRUISE_DRP, 'options'),
             Output(SELECT_CRUISE_DRP, 'value')],
            [Input(SELECT_COLLECTION_DRP, 'value')],

        )
        def update_selected_value(selected_collection):
            self.feature_handler.select_collection(selected_collection)
            nested_level_values = self.feature_handler.get_nested_level_values(selected_collection)
            cruises = list(nested_level_values.keys())
            return cruises, cruises[0]

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def get(self, sub_component: str, sub_component_id_str, sub_config: Dict) -> Component:
        collections = self.feature_handler.get_collections()
        default_value = self.feature_handler.get_collections()[0]
        return html.Div([
            FormLabel("Select Data Collection: ",
                      style={'marginRight': '20px',
                             'fontSize': 'larger',
                             'fontWeight': 'bold'}
                      ),
            dcc.Dropdown(
                id=SELECT_COLLECTION_DRP,
                options=collections,
                value=default_value,
                style={'width': '400px', 'fontSize': 'x-large'}
            )
        ],
            style={'display': 'flex',
                   'alignItems': 'center',
                   'padding': '30px 0px 0px 50px'
                   }
        )
