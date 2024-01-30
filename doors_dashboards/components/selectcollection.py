from typing import Dict, List
from dash import dcc, html, Dash
import plotly.express as px
from dash.development.base_component import Component
import dash_bootstrap_components as dbc
from dash_material_ui import FormLabel

from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

SCATTER_PLOT_ID = 'scatter-plot'
SCATTER_PLOT_LINE_ID = 'scatter-plot'
SELECT_CRUISE_DRP = 'cruise-drpdown'
SELECT_STATION_DRP = 'station-drpdwn'
PLOT_BGCOLOR = 'rgb(91,157,181)'


class ScatterplotComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None

    def register_callbacks(self, app: Dash, component_ids: List[str]):
        pass

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def get(self, sub_component: str, sub_component_id_str, sub_config: Dict) -> Component:
        collection = self.feature_handler.get_collections()[0]
        df = self.feature_handler.get_df(collection)
        fig = px.scatter(
            df,
            x='temperature [°c]',
            y='salinity [psu]',
            color='station',
            color_discrete_sequence=px.colors.qualitative.Set1,  # Use a qualitative color scale
            labels={'temperature [°c]': 'Temperature (°C)', 'salinity [psu]': 'Salinity (psu)'},

        )
        fig.update_traces(marker_size=10)
        fig.layout.plot_bgcolor = PLOT_BGCOLOR
        # fig.update_traces(textposition="bottom right")
        if sub_component == "scatterplot_selection":
            return self._get_selection(collection)
        lineplot_fig = self.get_line_scatter_plot(collection)
        if len(self.feature_handler.get_variables(collection)) > 1:
            return html.Div(
                [
                    dcc.Graph(
                        id=SCATTER_PLOT_ID,
                        figure=fig,
                        style={
                            'height': '30vh'
                        },
                    ),
                    dcc.Graph(
                        id=SCATTER_PLOT_LINE_ID,
                        figure=lineplot_fig,
                        style={
                            'height': '40vh'
                        },
                    )
                ],
                style={
                    'display': 'flex',
                    "flexDirection": "column"

                }
            )
        else:
            return dcc.Graph(
                id=SCATTER_PLOT_LINE_ID,
                figure=lineplot_fig,
                style={
                    'height': '40vh'
                },
            )

    def get_line_scatter_plot(self, collection: List[str]):
        df = self.feature_handler.get_df(collection)
        fig = px.line(
            df,
            x='temperature [°c]',
            y='salinity [psu]',
            color='station',
            color_discrete_sequence=px.colors.qualitative.Set1,  # Use a qualitative color scale
            labels={'temperature [°c]': 'Temperature (°C)', 'salinity [psu]': 'Salinity (psu)'},

        )
        fig.update_traces(marker_size=10)
        fig.layout.plot_bgcolor = PLOT_BGCOLOR
        # fig.update_traces(textposition="bottom right")
        return fig

    @staticmethod
    def _get_selection(df):
        return html.Div([
            FormLabel("Select Cruise: ",
                      style={'marginRight': '20px',
                             'fontSize': 'x-large',
                             'fontWeight': 'bold'}
                      ),
            dcc.Dropdown(
                id=SELECT_CRUISE_DRP,
                options=[
                    {'label': 'classical_10d', 'value': 'classical_10d'},
                    {'label': 'classical_15d', 'value': 'classical_15d'},
                    {'label': 'classical_15d_with_climate',
                     'value': 'classical_15d_with_climate'},
                    {'label': 'classical_plume',
                     'value': 'classical_plume'},
                    {'label': 'classical_wave', 'value': 'classical_wave'}
                ],
                value='classical_wave',  # Default selected value
                style={'width': '300px', 'fontSize': 'x-large'}
            ),
            FormLabel("Select Station: ",
                      style={'marginLeft': '140px',
                             'fontSize': 'x-large',
                             'fontWeight': 'bold'}
                      ),
            dcc.Dropdown(
                id=SELECT_STATION_DRP,
                options=[
                    {'label': 'classical_10d', 'value': 'classical_10d'},
                    {'label': 'classical_15d', 'value': 'classical_15d'},
                    {'label': 'classical_15d_with_climate',
                     'value': 'classical_15d_with_climate'},
                    {'label': 'classical_plume',
                     'value': 'classical_plume'},
                    {'label': 'classical_wave', 'value': 'classical_wave'}
                ],
                value='classical_wave',  # Default selected value
                style={'marginLeft': '5px', 'width': '300px', 'fontSize': 'x-large'}
            ),
        ],
            style={'display': 'flex',
                   'alignItems': 'center',
                   'padding': '30px 0px 0px 50px'
                   }
        )
