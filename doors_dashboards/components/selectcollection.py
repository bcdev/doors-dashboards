from typing import Dict, List
from dash import dcc, html, Dash
import plotly.express as px
from dash.development.base_component import Component
from dash_material_ui import FormLabel

from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

SCATTER_PLOT_ID = 'scatter-plot'
SCATTER_PLOT_LINE_ID = 'scatter-plot'
SELECT_CRUISE_DRP = 'cruise-drpdown'
SELECT_STATION_DRP = 'station-drpdwn'
PLOT_BGCOLOR = 'rgb(91,157,181)'


class SelectCollectionComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None

    def register_callbacks(self, app: Dash, component_ids: List[str]):
        pass

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def get(self, sub_component: str, sub_component_id_str, sub_config: Dict) -> Component:
        collections = self.feature_handler.get_collections()
        default_value = self.feature_handler.get_collections()[0]
        return html.Div([
            FormLabel("Select Data Collection: ",
                      style={'marginRight': '20px',
                             'fontSize': 'x-large',
                             'fontWeight': 'bold'}
                      ),
            dcc.Dropdown(
                id=SELECT_CRUISE_DRP,
                options=collections,
                value=default_value,
                style={'width': '300px', 'fontSize': 'x-large'}
            )
        ],
            style={'display': 'flex',
                   'alignItems': 'center',
                   'padding': '30px 0px 0px 50px'
                   }
        )
