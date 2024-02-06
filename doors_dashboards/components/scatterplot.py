from typing import Dict, List
from dash import dcc, html, Dash, Input, Output, dash
import plotly.express as px
from dash.development.base_component import Component
import dash_bootstrap_components as dbc

from doors_dashboards.components.constant import SELECT_CRUISE_DRP, SELECT_STATION_DRP, SCATTER_PLOT_ID, \
    SCATTER_PLOT_LINE_ID
from doors_dashboards.components.selectcollection import SELECT_COLLECTION_DRP
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

PLOT_BGCOLOR = '#3B4758'
DISPLAY_STYLE = {'height': '45vh', 'border-radius': '15px', 'backgroundColor': PLOT_BGCOLOR}
DEFAULT_STATION = ""
DEFAULT_CRUISE = ""


class ScatterplotComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def get(self, sub_component: str, sub_component_id_str, sub_config: Dict) -> Component:
        collection = self.feature_handler.get_selected_collection()
        # For dropdown selection part
        if sub_component == "scatterplot_selection":
            return self._get_selection(self, collection)
        # For rendering scatterplots
        pointplot_fig = self.get_point_scatter_plot(collection)
        lineplot_fig = self.get_line_scatter_plot(collection)
        if len(self.feature_handler.get_variables(collection)) > 1:
            return dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        id=SCATTER_PLOT_ID,
                        figure=pointplot_fig,
                        style=DISPLAY_STYLE,
                    ),
                    className='col-lg-12 rounded',
                    style={'marginBottom': '15px'}
                ),
                html.Div(className="w-100"),
                dbc.Col(
                    dcc.Graph(
                        id=SCATTER_PLOT_LINE_ID,
                        figure=lineplot_fig,
                        style=DISPLAY_STYLE
                    ),
                    width=4,
                    className='col-lg-12 rounded',
                    # style={'opacity': '0.5'}
                ),
            ]
            )
        else:
            return dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id=SCATTER_PLOT_ID,
                            figure=pointplot_fig,
                            style={'display': 'None'},
                        ),
                        className='col-lg-12 rounded',
                        # style={'opacity': '0.5'}
                    ),
                    dbc.Col(
                        dcc.Graph(
                            id=SCATTER_PLOT_LINE_ID,
                            figure=lineplot_fig,
                            style=DISPLAY_STYLE
                        ),
                        className='col-lg-12 rounded',
                        # style={'opacity': '0.5'}
                    ),
                ],
            )

    def get_point_scatter_plot(self, collection: str, selected_station: str = "", selected_cruise: str = ""):
        df = self.getdataframe(collection, selected_station, selected_cruise)
        variables = self.feature_handler.get_variables(collection)
        if len(variables) > 1:
            fig = px.scatter(
                df,
                x=variables[0],
                y=variables[1],
                color='sampling depth [m]',
                color_discrete_sequence=px.colors.qualitative.Set1,  # Use a qualitative color scale
            )
            fig.update_layout(font=dict(family="Roboto, Helvetica, Arial, sans-serif", size=18, color="white"))
            fig.update_traces(marker_size=10)
            fig.layout.plot_bgcolor = "rgb(0,0,0,0)"
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            fig.update_layout(legend_font_family="Roboto, Helvetica, Arial, sans-serif")
            return fig

    def get_line_scatter_plot(self, collection: str, selected_cruise: str = "", selected_station: str = "", ):
        df = self.getdataframe(collection, selected_station, selected_cruise)
        variable = self.feature_handler.get_variables(collection)[0]
        fig = px.line(
            df,
            x=variable,
            y='sampling depth [m]',
            color='cruise',
        )
        fig.update_yaxes(autorange='reversed')
        fig.update_layout(font=dict(family="Roboto, Helvetica, Arial, sans-serif", size=18, color="white"))
        fig.update_traces(marker_size=10)
        fig.layout.plot_bgcolor = "rgb(0,0,0,0)"
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        fig.update_layout(legend_font_family="Roboto, Helvetica, Arial, sans-serif")
        return fig

    def getdataframe(self, collection: str, selected_cruise: str, selected_station: str):
        df = self.feature_handler.get_df(collection)
        nested_level_values = self.feature_handler.get_nested_level_values(collection)
        cruises = list(nested_level_values.keys())
        cruises.sort()
        stations = list(nested_level_values.get(cruises[0]).keys())
        DEFAULT_CRUISE = cruises[0]
        DEFAULT_STATION = stations[0]
        if selected_cruise != "":
            df = df[df['cruise'] == selected_cruise]
        else:
            selected_cruise = DEFAULT_CRUISE
            df = df[df['cruise'] == selected_cruise]
        if selected_station != "":
            df = df[df['station'] == selected_station]
        else:
            selected_station = DEFAULT_STATION
            df = df[df['station'] == selected_station]
        return df

    @staticmethod
    def _get_selection(self, collection: List[str]):
        nested_level_values = self.feature_handler.get_nested_level_values(collection)
        cruises = list(nested_level_values.keys())
        cruises.sort()
        stations = list(nested_level_values.get(cruises[0]).keys())
        stations.sort()
        return dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.DropdownMenu(
                            id=SELECT_CRUISE_DRP,
                            label="Select Cruise",
                            children=[dbc.DropdownMenuItem(cruise, id='cruise_drp_option', n_clicks=0) for cruise in cruises],
                            style={'fontSize': 'x-large'},
                            size="lg"
                        )
                    ],
                    width=3,
                    className='mb-2'
                ),
                dbc.Col(
                    [
                        dbc.Label("Select Station:", className='mr-2',
                                  style={'fontSize': 'larger', 'fontWeight': 'bold', 'color': 'white'}),
                        dcc.Dropdown(
                            id=SELECT_STATION_DRP,
                            options=stations,
                            value=stations[0],  # Default selected value
                            style={'fontSize': 'x-large'}  # 'width': '300px', 'height': '40px',
                        ),
                    ],
                    width=3,
                    className='mb-2'
                )
            ],
        )

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

        @app.callback(
            [Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
             Output(SCATTER_PLOT_LINE_ID, 'figure', allow_duplicate=True)],
            [Input(SELECT_COLLECTION_DRP, 'value'),
             Input(SELECT_CRUISE_DRP, 'value'), Input(SELECT_STATION_DRP, 'value')],
            prevent_initial_call=True
        )
        def update_scatterplots(selected_collection, selected_cruise, selected_station):
            variables = self.feature_handler.get_variables(selected_collection)
            if len(variables) > 1:
                pointplot_fig = self.get_point_scatter_plot(selected_collection, selected_cruise, selected_station)
                lineplot_fig = self.get_line_scatter_plot(selected_collection)
            else:
                pointplot_fig = None
                lineplot_fig = self.get_line_scatter_plot(selected_collection)
            return pointplot_fig, lineplot_fig
