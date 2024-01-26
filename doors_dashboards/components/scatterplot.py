from typing import Dict, List

import dash
from dash import dcc, html, Dash
import plotly.express as px
import pandas as pd
from dash.development.base_component import Component

from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

SCATTER_PLOT_ID = 'scatter-plot'

# Given data
data = {
    'temperature [°c]': [18.04, 17.04, 8.78, 8.58, 8.67],
    'salinity [psu]': [18.159, 18.304, 18.474, 19.6, 20.576],
    'longitude': [31.7105, 31.7105, 31.7105, 31.7105, 31.7105],
    'latitude': [43.7538, 43.7538, 43.7538, 43.7538, 43.7538],
    'station': ['JOSS GE-UA - 1', 'JOSS GE-UA - 1', 'JOSS GE-UA - 1', 'JOSS GE-UA - 1', 'JBSS GE-UA - 12'],
}

df = pd.DataFrame(data)


class ScatterplotComponent(DashboardComponent):

    def register_callbacks(self, app: Dash, component_ids: List[str]):
        pass

    def set_feature_handler(self, feature_handler: FeatureHandler):
        pass

    def get(self, sub_component: str, sub_component_id_str, sub_config: Dict) -> Component:
        fig = px.line(
            df,
            x='temperature [°c]',
            y='salinity [psu]',
            color='station',
            color_discrete_sequence=px.colors.qualitative.Set1,  # Use a qualitative color scale
            labels={'temperature [°c]': 'Temperature (°C)', 'salinity [psu]': 'Salinity (psu)'},
            text='station'
        )
        fig.update_traces(marker_size=10)
        fig.update_traces(textposition="bottom right")

        return dcc.Graph(
            id=SCATTER_PLOT_ID,
            figure=fig
        )
