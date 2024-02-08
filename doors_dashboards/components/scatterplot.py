from typing import Dict, List
from dash import dcc, html, Dash, Input, Output, dash
import plotly.express as px
from dash.development.base_component import Component
import dash_bootstrap_components as dbc

from doors_dashboards.components.constant import SELECT_CRUISE_DRP, SELECT_STATION_DRP, \
    SCATTER_PLOT_ID, \
    SCATTER_PLOT_LINE_ID, PLOT_BGCOLOR, FONT_FAMILY, FONT_COLOR
from doors_dashboards.components.selectcollection import SELECT_COLLECTION_DRP
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

DISPLAY_STYLE = {'height': '45vh'}
DEFAULT_STATION = ""
DEFAULT_CRUISE = ""


class ScatterplotComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def get(self, sub_component: str, sub_component_id_str,
            sub_config: Dict) -> Component:
        collection = self.feature_handler.get_selected_collection()
        # For rendering scatterplots
        pointplot_fig = self.get_point_scatter_plot(collection)
        lineplot_fig = self.get_line_scatter_plot(collection)
        nested_level_values = self.feature_handler.get_nested_level_values(collection)
        cruises = list(nested_level_values.keys())
        cruises.sort()
        stations = list(nested_level_values.get(cruises[0]).keys())
        stations.sort()
        if len(self.feature_handler.get_variables(collection)) > 1:
            return dbc.Row([
                dbc.Col(
                    html.Div(
                        [
                            dbc.DropdownMenu(
                                id=SELECT_CRUISE_DRP,
                                label=cruises[0],
                                children=[
                                    dbc.DropdownMenuItem(cruise,
                                                         id=f'cruise_drp_option_{i}',
                                                         n_clicks=1) for i, cruise
                                    in
                                    enumerate(cruises)],
                                style={
                                    'fontfamily': FONT_FAMILY,
                                    'font-size': 'x-large'},
                                size="lg",
                                className="float-right",
                                color="secondary"
                            ),
                            dcc.Graph(
                                id=SCATTER_PLOT_LINE_ID,
                                figure=lineplot_fig,
                                style=DISPLAY_STYLE
                            ),
                        ],
                        style={'backgroundColor': PLOT_BGCOLOR, 'padding': '10px',
                               'border-radius': '15px'}
                    ),
                    className='col-lg-12',
                    style={'marginBottom': '15px'}
                ),
                html.Div(className="w-100"),
                dbc.Col(
                    html.Div(
                        [
                            dbc.DropdownMenu(
                                id=SELECT_STATION_DRP,
                                label=stations[0],
                                children=[
                                    dbc.DropdownMenuItem(station,
                                                         id=f'station_drp_option_{i}',
                                                         n_clicks=1) for i, station
                                    in
                                    enumerate(stations)],
                                style={
                                    'fontfamily': FONT_FAMILY,
                                    'font-size': 'x-large'},
                                size="lg",
                                className="float-right",
                                color="secondary"
                            ),
                            dcc.Graph(
                                id=SCATTER_PLOT_ID,
                                figure=pointplot_fig,
                                style=DISPLAY_STYLE,
                            ),
                        ],
                        style={'backgroundColor': PLOT_BGCOLOR, 'padding': '10px',
                               'border-radius': '15px'}
                    ),
                    className='col-lg-12',
                    style={'marginBottom': '15px'}
                ),
            ]
            )
        else:
            return dbc.Row([
                dbc.Col(
                    html.Div(
                        [
                            dbc.DropdownMenu(
                                id=SELECT_CRUISE_DRP,
                                label=cruises[0],
                                children=[
                                    dbc.DropdownMenuItem(cruise,
                                                         id=f'cruise_drp_option_{i}',
                                                         n_clicks=1) for i, cruise
                                    in
                                    enumerate(cruises)],
                                style={
                                    'fontfamily': FONT_FAMILY,
                                    'font-size': 'x-large'},
                                size="lg",
                                className="float-right",
                                color="secondary"
                            ),
                            dcc.Graph(
                                id=SCATTER_PLOT_LINE_ID,
                                figure=lineplot_fig,
                                style=DISPLAY_STYLE
                            ),
                        ],
                        style={'backgroundColor': PLOT_BGCOLOR, 'padding': '10px',
                               'border-radius': '15px'}
                    ),
                    className='col-lg-12',
                    style={'marginBottom': '15px'}
                ),
                html.Div(className="w-100"),
                dbc.Col(
                    html.Div(
                        [
                            dbc.DropdownMenu(
                                id=SELECT_STATION_DRP,
                                label=stations[0],
                                children=[
                                    dbc.DropdownMenuItem(station,
                                                         id=f'station_drp_option_{i}',
                                                         n_clicks=1) for i, station
                                    in
                                    enumerate(stations)],
                                style={
                                    'fontfamily': FONT_FAMILY,
                                    'font-size': 'x-large'},
                                size="lg",
                                className="float-right",
                                color="secondary"
                            ),
                            dcc.Graph(
                                id=SCATTER_PLOT_ID,
                                figure=pointplot_fig,
                                style=DISPLAY_STYLE,
                            ),
                        ],
                        style={'backgroundColor': PLOT_BGCOLOR, 'padding': '10px',
                               'border-radius': '15px'}
                    ),
                    className='col-lg-12',
                    style={'marginBottom': '15px', 'display': 'None'}
                ),
            ]
            )

    def get_point_scatter_plot(self, collection: str, selected_station: str = "",
                               selected_cruise: str = ""):
        df = self.getdataframe(collection, selected_station, selected_cruise)
        variables = self.feature_handler.get_variables(collection)
        if len(variables) > 1:
            fig = px.scatter(
                df,
                x=variables[0],
                y=variables[1],
                color='sampling depth [m]',
                color_discrete_sequence=px.colors.qualitative.Set1,
                # Use a qualitative color scale
            )
            fig.update_layout(
                font=dict(family=FONT_FAMILY, size=18,
                          color=FONT_COLOR))
            fig.update_traces(marker_size=10)
            fig.layout.plot_bgcolor = "rgb(0,0,0,0)"
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            fig.update_layout(legend_font_family="Roboto, Helvetica, Arial, sans-serif")
            return fig

    def get_line_scatter_plot(self, collection: str, selected_cruise: str = "",
                              selected_station: str = "", ):
        df = self.getdataframe(collection, selected_station, selected_cruise)
        variable = self.feature_handler.get_variables(collection)[0]
        fig = px.line(
            df,
            x=variable,
            y='sampling depth [m]',
            color='cruise',
        )
        fig.update_yaxes(autorange='reversed')
        fig.update_layout(
            font=dict(family=FONT_FAMILY, size=18,
                      color=FONT_COLOR))
        fig.update_traces(marker_size=10)
        fig.layout.plot_bgcolor = "rgb(0,0,0,0)"
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        fig.update_layout(legend_font_family="Roboto, Helvetica, Arial, sans-serif")
        return fig

    def getdataframe(self, collection: str, selected_cruise: str,
                     selected_station: str):
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

    def register_callbacks(self, app: Dash, component_ids: List[str]):

        collection = self.feature_handler.get_selected_collection()
        nested_level_values = self.feature_handler.get_nested_level_values(collection)
        cruises = list(nested_level_values.keys())
        cruises.sort()
        dropdown_cruise_ids = [f'cruise_drp_option_{i}' for i in range(len(cruises))]

        @app.callback(
            [Output(SELECT_STATION_DRP, 'children', allow_duplicate=True),
             Output(SELECT_STATION_DRP, 'label', allow_duplicate=True),
             Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
             Output(SCATTER_PLOT_LINE_ID, 'figure', allow_duplicate=True)],
            [Input(dropdown_cruise_id, 'n_clicks_timestamp') for dropdown_cruise_id in
             dropdown_cruise_ids],
            prevent_initial_call=True
        )
        def updateDrpAndPlots(*timestamps):
            collection = self.feature_handler.get_selected_collection()
            nested_level_values = self.feature_handler.get_nested_level_values(
                collection)
            cruises = list(nested_level_values.keys())
            if any(timestamps):  # Check if any timestamp is not None
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                selected_cruise = cruises[latest_timestamp_index]

                stations = list(nested_level_values.get(selected_cruise).keys())
                stations.sort()
                station_dropdown_items = [
                    dbc.DropdownMenuItem(station,
                                         id=f'station_drp_option_{i}',
                                         n_clicks=1) for i, station in enumerate(
                        stations)
                ]
                variables = self.feature_handler.get_variables(collection)
                if len(variables) > 1:
                    pointplot_fig = self.get_point_scatter_plot(collection,
                                                                selected_cruise,
                                                                stations[0])
                    lineplot_fig = self.get_line_scatter_plot(collection,
                                                              selected_cruise,
                                                              stations[0])
                else:
                    pointplot_fig = None
                    lineplot_fig = self.get_line_scatter_plot(collection)
                return (station_dropdown_items, stations[0] if stations else None,
                        pointplot_fig, lineplot_fig)
            else:
                return dash.no_update

        @app.callback(
            Output(SELECT_CRUISE_DRP, 'label', allow_duplicate=True),
            # Update the label of the dropdown menu
            [Input(dropdown_cruise_id, 'n_clicks_timestamp') for dropdown_cruise_id in
             dropdown_cruise_ids],
            prevent_initial_call=True
        )
        def update_label(*timestamps):
            if any(timestamps):
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                selected_cruise = cruises[latest_timestamp_index]
                return selected_cruise
            else:
                return dash.no_update

        collections = self.feature_handler.get_collections()
        dropdown_ids = [f'collection_drp_option_{i}' for i in range(len(collections))]

        @app.callback(
            [Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
             Output(SCATTER_PLOT_LINE_ID, 'figure', allow_duplicate=True)],
            [Input(dropdown_id, 'n_clicks_timestamp') for dropdown_id in
             dropdown_ids],
            prevent_initial_call=True
        )
        def update_scatterplots(*timestamps):
            if any(timestamps):
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                selected_collection = collections[latest_timestamp_index]
                self.feature_handler.select_collection(selected_collection)
                variables = self.feature_handler.get_variables(selected_collection)
                nested_level_values = self.feature_handler.get_nested_level_values(
                    selected_collection)
                cruises = list(nested_level_values.keys())
                cruises.sort()
                stations = list(nested_level_values.get(cruises[0]).keys())
                stations.sort()
                if len(variables) > 1:
                    pointplot_fig = self.get_point_scatter_plot(selected_collection,
                                                                cruises[0],
                                                                stations[0])
                    lineplot_fig = self.get_line_scatter_plot(selected_collection,
                                                              cruises[0],stations[0])
                else:
                    pointplot_fig = None
                    lineplot_fig = self.get_line_scatter_plot(selected_collection)

            return pointplot_fig, lineplot_fig
