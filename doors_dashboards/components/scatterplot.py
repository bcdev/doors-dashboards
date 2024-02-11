from typing import Dict, List
from dash import dcc, html, Dash, Input, Output, dash
import plotly.express as px
from dash.development.base_component import Component
import dash_bootstrap_components as dbc

from doors_dashboards.components.constant import COLLECTION_TEMPLATE
from doors_dashboards.components.constant import FONT_COLOR
from doors_dashboards.components.constant import FONT_FAMILY
from doors_dashboards.components.constant import PLOT_BGCOLOR
from doors_dashboards.components.constant import SCATTER_PLOT_ID
from doors_dashboards.components.constant import SCATTER_PLOT_LINE_ID
from doors_dashboards.components.constant import SELECT_GROUP_DRP
from doors_dashboards.components.constant import SELECT_MAINGROUP_DRP
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

DISPLAY_STYLE = {'height': '45vh'}
GROUP_TEMPLATE = 'group_drp_option_{0}_{1}'
MAIN_GROUP_TEMPLATE = 'main_group_drp_option_{0}_{1}'

SELECTED_MAIN_GROUP_ITEM = ""


class ScatterplotComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    @staticmethod
    def _get_dropdown_menu(dropdown_id: str, id_template: str, values: List[str]
                           ) -> dbc.DropdownMenu:
        return dbc.DropdownMenu(
            id=dropdown_id,
            label=values[0],
            children=[
                dbc.DropdownMenuItem(v,
                                     id=id_template.format(i, v),
                                     n_clicks=1) for i, v in enumerate(values)],
            style={
                'fontfamily': FONT_FAMILY,
                'font-size': 'x-large'},
            size="lg",
            className="float-right",
            color="secondary"
        )

    def get(self, sub_component: str, sub_component_id_str,
            sub_config: Dict) -> Component:
        collection = self.feature_handler.get_selected_collection()
        # For rendering scatterplots
        group_values, main_group_values = \
            self._get_group_and_main_group_values(collection)
        pointplot_fig = self.get_point_scatter_plot(collection)
        lineplot_fig = self.get_line_scatter_plot(collection)

        group_dropdown_menu = self._get_dropdown_menu(
            SELECT_GROUP_DRP, GROUP_TEMPLATE, group_values
        )
        upper_components = [
            dcc.Graph(
                id=SCATTER_PLOT_LINE_ID, figure=lineplot_fig, style=DISPLAY_STYLE
            )
        ]
        if main_group_values is not None:
            global SELECTED_MAIN_GROUP_ITEM
            SELECTED_MAIN_GROUP_ITEM = main_group_values[0]
            maingroup_dropdown_menu = self._get_dropdown_menu(
                SELECT_MAINGROUP_DRP, MAIN_GROUP_TEMPLATE, main_group_values
            )
            upper_components.insert(0, maingroup_dropdown_menu)
        lower_components = []
        if len(self.feature_handler.get_variables(collection)) > 1:
            lower_components.append(group_dropdown_menu)
            lower_components.append(
                dcc.Graph(
                    id=SCATTER_PLOT_ID, figure=pointplot_fig, style=DISPLAY_STYLE
                )
            )
        sub_components = [
            dbc.Col(
                html.Div(upper_components,
                         style={'backgroundColor': PLOT_BGCOLOR,
                                'padding': '10px',
                                'border-radius': '15px'}
                         ),
                className='col-lg-12',
                style={'marginBottom': '15px'}
            ),
            html.Div(className="w-100")
        ]
        if len(lower_components) > 0:
            sub_components.append(
                dbc.Col(
                    html.Div(lower_components,
                             style={'backgroundColor': PLOT_BGCOLOR,
                                    'padding': '10px',
                                    'border-radius': '15px'}
                             ),
                    className='col-lg-12',
                    style={'marginBottom': '15px'}
                )
            )
        return dbc.Row(sub_components)

    def get_point_scatter_plot(self, collection: str,
                               selected_group_item: str = "",
                               selected_main_group_item: str = ""):
        df = self.get_dataframe(
            collection, selected_group_item, selected_main_group_item
        )
        levels = self.feature_handler.get_levels(collection)
        variables = self.feature_handler.get_variables(collection)
        if len(variables) > 1:
            fig = px.scatter(
                df,
                x=variables[0],
                y=variables[1],
                color=levels[-1],
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

    def get_line_scatter_plot(self, collection: str, selected_group_item: str = "",
                              selected_main_group_item: str = ""):
        df = self.get_dataframe(
            collection, selected_group_item, selected_main_group_item
        )
        levels = self.feature_handler.get_levels(collection)
        variable = self.feature_handler.get_variables(collection)[0]
        fig = px.line(
            df,
            x=variable,
            y=levels[-1],
            color=levels[-2],
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

    def _get_group_and_main_group_values(self, collection: str):
        levels = self.feature_handler.get_levels()
        nested_level_values = self.feature_handler.get_nested_level_values(collection)
        if len(levels) < 3:
            group_values = list(nested_level_values.keys())
            group_values.sort()
            return group_values, None
        else:
            main_group_values = list(nested_level_values.keys())
            main_group_values.sort()
            group_values = list(nested_level_values.get(main_group_values[0]).keys())
            group_values.sort()
            return group_values, main_group_values

    def _get_group_values_for_main_group(self, collection: str, main_group: str):
        nested_level_values = self.feature_handler.get_nested_level_values(collection)
        group_values = list(nested_level_values.get(main_group).keys())
        group_values.sort()
        return group_values


    def get_dataframe(self,
                      collection: str,
                      selected_group_item: str = "",
                      selected_main_group_item: str = ""
                      ):
        df = self.feature_handler.get_df(collection)
        group_values, main_group_values = \
            self._get_group_and_main_group_values(collection)
        levels = self.feature_handler.get_levels()
        if main_group_values is not None:
            main_group_item = selected_main_group_item \
                if selected_main_group_item != "" else main_group_values[0]
            df = df[df[levels[-3]] == main_group_item]
        group_item = selected_group_item \
            if selected_group_item != "" else group_values[0]
        df = df[df[levels[-2]] == group_item]
        return df

    def register_callbacks(self, app: Dash, component_ids: List[str]):

        collection = self.feature_handler.get_selected_collection()
        group_values, main_group_values = \
            self._get_group_and_main_group_values(collection)

        collections = self.feature_handler.get_collections()
        collection_ids = [COLLECTION_TEMPLATE.format(i, c)
                          for i, c in enumerate(collections)]

        group_value_ids = [GROUP_TEMPLATE.format(i, m)
                           for i, m in enumerate(group_values)]

        if main_group_values is not None:
            main_group_value_ids = [MAIN_GROUP_TEMPLATE.format(i, m)
                                    for i, m in enumerate(main_group_values)]
            @app.callback(
                [Output(SELECT_GROUP_DRP, 'children', allow_duplicate=True),
                 Output(SELECT_GROUP_DRP, 'label', allow_duplicate=True),
                 Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
                 Output(SCATTER_PLOT_LINE_ID, 'figure', allow_duplicate=True)],
                [Input(main_group_value_id, 'n_clicks_timestamp')
                 for main_group_value_id in main_group_value_ids],
                prevent_initial_call=True
            )
            def updateDropDownAndPlotsAfterMainGroupChange(*timestamps):
                collection = self.feature_handler.get_selected_collection()
                _, main_group_values = \
                    self._get_group_and_main_group_values(collection)
                if any(timestamps):  # Check if any timestamp is not None
                    latest_timestamp_index = timestamps.index(
                        max(t for t in timestamps if t is not None))
                    SELECTED_MAIN_GROUP_ITEM = main_group_values[latest_timestamp_index]
                    group_values = self._get_group_values_for_main_group(
                        collection, SELECTED_MAIN_GROUP_ITEM
                    )
                    group_dropdown_items = [
                        dbc.DropdownMenuItem(
                            group_member,
                            id=GROUP_TEMPLATE.format(i, group_member),
                            n_clicks=1) for i, group_member in enumerate(group_values)
                    ]
                    variables = self.feature_handler.get_variables(collection)
                    if len(variables) > 1:
                        pointplot_fig = self.get_point_scatter_plot(
                            collection, group_values[0], SELECTED_MAIN_GROUP_ITEM)
                        lineplot_fig = self.get_line_scatter_plot(
                            collection, group_values[0], SELECTED_MAIN_GROUP_ITEM
                        )
                    else:
                        pointplot_fig = None
                        lineplot_fig = self.get_line_scatter_plot(collection)
                    return (group_dropdown_items,
                            group_values[0] if group_values else None,
                            pointplot_fig,
                            lineplot_fig)
                else:
                    return dash.no_update

            @app.callback(
                Output(SELECT_MAINGROUP_DRP, 'label', allow_duplicate=True),
                # Update the label of the dropdown menu
                [Input(main_group_value_id, 'n_clicks_timestamp')
                 for main_group_value_id in main_group_value_ids],
                prevent_initial_call=True
            )
            def update_main_group_label(*timestamps):
                if any(timestamps):
                    latest_timestamp_index = timestamps.index(
                        max(t for t in timestamps if t is not None))
                    collection = self.feature_handler.get_selected_collection()
                    group_values, main_group_values = \
                        self._get_group_and_main_group_values(collection)
                    SELECTED_MAIN_GROUP_ITEM = main_group_values[latest_timestamp_index]
                    return SELECTED_MAIN_GROUP_ITEM
                else:
                    return dash.no_update

            @app.callback(
                [Output(SELECT_MAINGROUP_DRP, 'children'),
                Output(SELECT_MAINGROUP_DRP, 'label')],
                [Input(collection_id, 'n_clicks_timestamp')
                    for collection_id in collection_ids],
                prevent_initial_call=True
            )
            def update_selected_main_group_dropdown(*timestamps):
                if any(timestamps):
                    latest_timestamp_index = timestamps.index(
                        max(t for t in timestamps if t is not None))
                    selected_collection = collections[latest_timestamp_index]
                    self.feature_handler.select_collection(selected_collection)
                    group_values, main_group_values = \
                        self._get_group_and_main_group_values(selected_collection)
                    main_group_dropdown_items = [
                        dbc.DropdownMenuItem(
                            member, id=MAIN_GROUP_TEMPLATE.format(i, member),
                            n_clicks=1) for i, member in enumerate(main_group_values)
                    ]
                    SELECTED_MAIN_GROUP_ITEM = main_group_values[0]
                    return (main_group_dropdown_items, SELECTED_MAIN_GROUP_ITEM)
                else:
                    return dash.no_update

        @app.callback(
            Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
            [Input(group_value_id, 'n_clicks_timestamp')
                for group_value_id in group_value_ids],
            prevent_initial_call=True
        )
        def updatePointPlotAfterGroupChange(*timestamps):
            collection = self.feature_handler.get_selected_collection()
            group_values, _ = self._get_group_and_main_group_values(collection)
            if any(timestamps):  # Check if any timestamp is not None
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                group_item = group_values[latest_timestamp_index]
                variables = self.feature_handler.get_variables(collection)
                if len(variables) > 1:
                    return self.get_point_scatter_plot(
                        collection, group_item, SELECTED_MAIN_GROUP_ITEM
                    )
                else:
                    return None
            else:
                return dash.no_update

        @app.callback(
            Output(SELECT_GROUP_DRP, 'label', allow_duplicate=True),
            # Update the label of the dropdown menu
            [Input(group_value_id, 'n_clicks_timestamp')
                for group_value_id in group_value_ids],
            prevent_initial_call=True
        )
        def update_group_label(*timestamps):
            if any(timestamps):
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                collection = self.feature_handler.get_selected_collection()
                group_values, main_group_values = \
                    self._get_group_and_main_group_values(collection)
                return group_values[latest_timestamp_index]
            else:
                return dash.no_update

        @app.callback(
            [Output(SELECT_GROUP_DRP, 'children', allow_duplicate=True),
             Output(SELECT_GROUP_DRP, 'label', allow_duplicate=True)],
            [Input(collection_id, 'n_clicks_timestamp')
                for collection_id in collection_ids],
            prevent_initial_call=True
        )
        def update_selected_group_dropdown(*timestamps):
            if any(timestamps):
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                selected_collection = collections[latest_timestamp_index]
                self.feature_handler.select_collection(selected_collection)
                group_values, main_group_values = \
                    self._get_group_and_main_group_values(selected_collection)
                group_dropdown_items = [
                    dbc.DropdownMenuItem(
                        member,
                        id=GROUP_TEMPLATE.format(i, member),
                        n_clicks=1) for i, member in enumerate(group_values)
                ]
                return group_dropdown_items, group_values[0]
            else:
                return dash.no_update
