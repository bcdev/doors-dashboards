from typing import Dict, List
from dash import dcc, html, Dash, Input, Output, dash
import plotly.express as px
from dash.development.base_component import Component
from dash_material_ui import FormLabel

from doors_dashboards.components.constant import SELECT_CRUISE_DRP, SELECT_STATION_DRP, SCATTER_PLOT_ID, \
    SCATTER_PLOT_LINE_ID
from doors_dashboards.components.selectcollection import SELECT_COLLECTION_DRP
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler


PLOT_BGCOLOR = 'rgb(173,206,218)'


class ScatterplotComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None

    def register_callbacks(self, app: Dash, component_ids: List[str]):
        @app.callback(
            [Output(SELECT_STATION_DRP, 'options'),
             Output(SELECT_STATION_DRP, 'value')],
            [Input(SELECT_CRUISE_DRP, 'value')],
            prevent_initial_call=True
        )
        def update_stations(selected_cruise):
            collection = self.feature_handler.get_selected_collection()
            nested_level_values = self.feature_handler.get_nested_level_values(collection)
            cruises = list(nested_level_values.keys())
            cruises.sort()
            stations = list(nested_level_values.get(selected_cruise).keys())
            stations.sort()
            return stations, stations[0]



    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def get(self, sub_component: str, sub_component_id_str, sub_config: Dict) -> Component:
        collection = self.feature_handler.get_selected_collection()
        df = self.feature_handler.get_df(collection)
        pointplot_fig = self.get_point_scatter_plot(collection)
        if sub_component == "scatterplot_selection":
            return self._get_selection(self, collection)
        lineplot_fig = self.get_line_scatter_plot(collection)
        if len(self.feature_handler.get_variables(collection)) > 1:
            return html.Div(
                [
                    dcc.Graph(
                        id=SCATTER_PLOT_ID,
                        figure=pointplot_fig,
                        style={
                            'height': '40vh'
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

    def get_point_scatter_plot(self, collection: List[str]):
        df = self.feature_handler.get_df(collection)
        variables = self.feature_handler.get_variables(collection)
        if len(variables) > 1:
            fig = px.scatter(
                df,
                x=variables[0],
                y=variables[1],
                color='sampling depth [m]',
                color_discrete_sequence=px.colors.qualitative.Set1,  # Use a qualitative color scale
            )
            fig.update_layout(font=dict(family="Roboto, Helvetica, Arial, sans-serif", size=18, color="rgb(0, 0, 0)"))
            fig.update_traces(marker_size=10)
            fig.layout.plot_bgcolor = PLOT_BGCOLOR
            return fig

    def get_line_scatter_plot(self, collection: List[str]):
        df = self.feature_handler.get_df(collection)
        # df = df[df["cruise"] == "NPMS GE 2016"]
        variable = self.feature_handler.get_variables(collection)[0]
        fig = px.line(
            df,
            x=variable,
            y='sampling depth [m]',
            color='station',
            color_discrete_sequence=px.colors.qualitative.Set1,  # Use a qualitative color scale
            # labels={'temperature [°c]': 'Temperature (°C)', 'sampling depth [m]': 'Sampling depth [m]'},

        )
        fig.update_yaxes(autorange='reversed')
        fig.update_layout(font=dict(family="Roboto, Helvetica, Arial, sans-serif", size=18, color="rgb(0, 0, 0)"))
        fig.update_traces(marker_size=10)
        fig.layout.plot_bgcolor = PLOT_BGCOLOR
        return fig

    @staticmethod
    def _get_selection(self, collection: List[str]):
        nested_level_values = self.feature_handler.get_nested_level_values(collection)
        cruises = list(nested_level_values.keys())
        cruises.sort()
        stations = list(nested_level_values.get(cruises[0]).keys())
        stations.sort()

        return html.Div(
            [
                FormLabel("Select Cruise: ",
                          style={'marginRight': '15px',
                                 'fontSize': 'larger',
                                 'fontWeight': 'bold'}
                          ),
                dcc.Dropdown(
                    id=SELECT_CRUISE_DRP,
                    options=cruises,
                    value=cruises[0],  # Default selected value
                    style={'width': '300px', 'height': '40px', 'fontSize': 'x-large'}
                ),
                FormLabel("Select Station: ",
                          style={'marginLeft': '80px',
                                 'fontSize': 'larger',
                                 'fontWeight': 'bold'}
                          ),
                dcc.Dropdown(
                    id=SELECT_STATION_DRP,
                    options=stations,
                    value=stations[0],  # Default selected value
                    style={'marginLeft': '5px', 'width': '300px', 'height': '40px', 'fontSize': 'x-large'}
                ),
                # dcc.LogoutButton(id='btnVisualise', label="Visualise", style={'width': '300px', 'fontFamily': 'Roboto, Helvetica, Arial, sans-serif', 'marginLeft': '100px', 'font-size': 'larger', 'background-color': 'rgb(12, 80, 111)', 'border': 'none'})
            ],
            style={'display': 'flex',
                   'alignItems': 'center',
                   'padding': '30px 0px 0px 50px'
                   }
        )
