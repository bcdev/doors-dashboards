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
from doors_dashboards.components.constant import GROUP_DROPDOWN_TEMPLATE
from doors_dashboards.components.constant import MAINGROUP_DROPDOWN_TEMPLATE
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

DISPLAY_STYLE = {'height': '45vh'}
GROUP_DROP_OPTION_TEMPLATE = 'group_drp_option_{0}_{1}_{2}'
MAIN_GROUP_DROP_OPTION_TEMPLATE = 'main_group_drp_option_{0}_{1}'

COLLAPSE = "collapse_id"

ALL_GROUP_MEMBERS = "all"
SELECTED_MAIN_GROUP_ITEM = ""


class ScatterplotComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None
        self.group_ids_per_main_group = dict()
        self.all_group_ids = []
        self.dropdown_menus = {}
        self.group_dropdown_menus = dict()
        self.group_drop_options = dict()
        self.main_group_dropdown_menus = dict()
        self.main_group_drop_options = dict()

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler
        # self._set_up_group_ids()

    @staticmethod
    def _get_dropdown_menu(
            dropdown_id: str, items: List[dbc.DropdownMenuItem], default: str
    ) -> dbc.DropdownMenu:
        return dbc.DropdownMenu(
            id=dropdown_id,
            label=default,
            children=items,
            style={
                'fontfamily': FONT_FAMILY,
                'font-size': 'x-large',
                'display': 'none'
            },
            color="secondary"
        )

    def _setup_dropdown_menus(self):
        collections = self.feature_handler.get_collections()
        for collection in collections:
            group_values, main_group_values = \
                self._get_group_and_main_group_values(collection)
            if main_group_values is not None:
                dropdown_main_menu_items = []
                for main_group in main_group_values:
                    # set up main group drop options
                    main_group_drop_option_id = MAIN_GROUP_DROP_OPTION_TEMPLATE.format(
                        collection, main_group
                    )
                    main_group_drop_option = dbc.DropdownMenuItem(
                        main_group,
                        id=main_group_drop_option_id,
                        n_clicks=1
                    )
                    self.main_group_drop_options[main_group_drop_option_id] = \
                        main_group_drop_option
                    dropdown_main_menu_items.append(main_group_drop_option)
                    # set up group drop options
                    groups = self._get_group_values_for_main_group(
                        collection, main_group
                    )
                    group_dropdown_menu_items = []
                    for member in groups:
                        group_drop_option_id = \
                            GROUP_DROP_OPTION_TEMPLATE.format(
                                collection, main_group, member
                            )
                        group_drop_down_menu_item = dbc.DropdownMenuItem(
                                member,
                                id=group_drop_option_id,
                                n_clicks=1
                            )
                        self.group_drop_options[group_drop_option_id] = \
                            group_drop_down_menu_item
                        group_dropdown_menu_items.append(group_drop_down_menu_item)
                    group_dropdown_id = \
                        GROUP_DROPDOWN_TEMPLATE.format(collection, main_group)
                    self.group_dropdown_menus[group_dropdown_id] = \
                        self._get_dropdown_menu(
                            GROUP_DROPDOWN_TEMPLATE.format(collection, main_group),
                            group_dropdown_menu_items,
                            groups[0]
                        )
                main_group_dropdown_id = MAINGROUP_DROPDOWN_TEMPLATE.format(collection)
                self.main_group_dropdown_menus[main_group_dropdown_id] = \
                    self._get_dropdown_menu(
                        MAINGROUP_DROPDOWN_TEMPLATE.format(collection),
                        dropdown_main_menu_items,
                        main_group_values[0]
                    )
            else:
                dropdown_menu_items = []
                for member in group_values:
                    group_drop_option_id = GROUP_DROP_OPTION_TEMPLATE.format(
                        collection, "all", member
                    )
                    group_drop_option = \
                        dbc.DropdownMenuItem(
                            member,
                            id=group_drop_option_id,
                            n_clicks=1
                        )
                    dropdown_menu_items.append(group_drop_option)
                    self.group_drop_options[group_drop_option_id] = group_drop_option
                group_dropdown_id = \
                    GROUP_DROPDOWN_TEMPLATE.format(collection, "all")
                self.group_dropdown_menus[group_dropdown_id] = \
                    self._get_dropdown_menu(
                        GROUP_DROPDOWN_TEMPLATE.format(collection, "all"),
                        dropdown_menu_items,
                        group_values[0]
                    )

    def get(self, sub_component: str, sub_component_id_str,
            sub_config: Dict) -> Component:
        self._setup_dropdown_menus()
        collection = self.feature_handler.get_selected_collection()
        # For rendering scatterplots
        pointplot_fig = self.get_point_scatter_plot(collection)
        lineplot_fig = self.get_line_scatter_plot(collection)

        global SELECTED_MAIN_GROUP_ITEM
        SELECTED_MAIN_GROUP_ITEM = "all"
        main_group_drop_down_menus = \
            list(self.main_group_dropdown_menus.values())
        if len(main_group_drop_down_menus) > 0:
            main_group_drop_down_menus[0].style['display'] = 'block'
            main_group_drop_options = list(self.main_group_drop_options.values())
            SELECTED_MAIN_GROUP_ITEM = main_group_drop_options[0].children



        upper_row = dbc.Row(
            children=main_group_drop_down_menus
        )
        upper_components = [
            upper_row,
            dcc.Graph(
                id=SCATTER_PLOT_LINE_ID, figure=lineplot_fig, style=DISPLAY_STYLE
            )
        ]
        group_drop_down_menus = list(self.group_dropdown_menus.values())
        group_drop_down_menus[0].style['display'] = 'block'
        lower_row = dbc.Row(
            children=group_drop_down_menus
        )
        lower_components = [
            lower_row,
            dcc.Graph(
                id=SCATTER_PLOT_ID, figure=pointplot_fig, style=DISPLAY_STYLE
            )
        ]
        sub_components = [
            dbc.Col(
                html.Div(upper_components,
                         style={'backgroundColor': PLOT_BGCOLOR,
                                'padding': '10px',
                                'border-radius': '15px'}
                         ),
                className='col-lg-12',
                style={'marginBottom': '15px'
                       },
            ),
            html.Div(className="w-100"),
            dbc.Collapse(
                id=COLLAPSE,
                children=dbc.Col(
                    html.Div(lower_components,
                             style={'backgroundColor': PLOT_BGCOLOR,
                                    'padding': '10px',
                                    'border-radius': '15px',
                                    }
                             ),
                    className='col-lg-12',
                    style={'marginBottom': '15px'}
                ),
                is_open=len(lower_components) > 0
            )
        ]
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

    def get_line_scatter_plot(self, collection: str, selected_main_group_item: str = ""):
        df = self.get_dataframe(
            collection, ALL_GROUP_MEMBERS, selected_main_group_item
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
        if selected_group_item != ALL_GROUP_MEMBERS:
            group_item = selected_group_item \
                if selected_group_item != "" else group_values[0]
            df = df[df[levels[-2]] == group_item]
        return df

    def register_callbacks(self, app: Dash, component_ids: List[str]):

        collection = self.feature_handler.get_selected_collection()
        group_values, main_group_values = \
            self._get_group_and_main_group_values(collection)

        collections = self.feature_handler.get_collections()
        collection_ids = [COLLECTION_TEMPLATE.format(c) for c in collections]

        group_dropdown_menus = list(self.group_dropdown_menus.keys())
        group_drop_options = list(self.group_drop_options.keys())

        if main_group_values is not None:
            main_group_dropdown_menus = list(self.main_group_dropdown_menus.keys())
            main_group_drop_options = list(self.main_group_drop_options.keys())

            style_outputs = [Output(group_dropdown_menu, 'style')
                for group_dropdown_menu in group_dropdown_menus]
            label_outputs = [
                Output(group_dropdown_menu, 'label', allow_duplicate=True)
                for group_dropdown_menu in group_dropdown_menus]
            outputs = style_outputs + label_outputs

            @app.callback(
                outputs,
                [Input(main_group_value_id, 'n_clicks_timestamp')
                    for main_group_value_id in main_group_drop_options],
                prevent_initial_call=True
            )
            def update_dropdown_after_main_group_change(*timestamps):
                if not any(timestamps):  # Check if any timestamp is not None
                    return dash.no_update

                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))

                main_group_id = \
                    list(self.main_group_drop_options.keys())[latest_timestamp_index]

                global SELECTED_MAIN_GROUP_ITEM
                SELECTED_MAIN_GROUP_ITEM = \
                    self.main_group_drop_options[main_group_id].children

                group_values = self._get_group_values_for_main_group(
                    collection, SELECTED_MAIN_GROUP_ITEM
                )

                valid_group_id = \
                    GROUP_DROPDOWN_TEMPLATE.format(collection, SELECTED_MAIN_GROUP_ITEM)

                results = []
                for group_dropdown_menu_id, group_dropdown_menu \
                        in self.group_dropdown_menus.items():
                    if group_dropdown_menu_id == valid_group_id:
                        results.append({'display': 'block'})
                    else:
                        results.append({'display': 'none'})
                for group_dropdown_menu_id, group_dropdown_menu \
                        in self.group_dropdown_menus.items():
                    if group_dropdown_menu_id == valid_group_id:
                        results.append(group_values[0])
                    else:
                        results.append('')
                return tuple(results)

            @app.callback(
                [Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
                 Output(SCATTER_PLOT_LINE_ID, 'figure', allow_duplicate=True)],
                [Input(main_group_value_id, 'n_clicks_timestamp')
                    for main_group_value_id in main_group_drop_options],
                prevent_initial_call=True
            )
            def update_plots_after_main_group_change(*timestamps):
                collection = self.feature_handler.get_selected_collection()
                if not any(timestamps):  # Check if any timestamp is not None
                    return dash.no_update
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))

                main_group_id = \
                    list(self.main_group_drop_options.keys())[latest_timestamp_index]

                global SELECTED_MAIN_GROUP_ITEM
                SELECTED_MAIN_GROUP_ITEM = \
                    self.main_group_drop_options[main_group_id].children

                group_values = self._get_group_values_for_main_group(
                    collection, SELECTED_MAIN_GROUP_ITEM
                )

                variables = self.feature_handler.get_variables(collection)
                if len(variables) > 1:
                    pointplot_fig = self.get_point_scatter_plot(
                        collection, group_values[0], SELECTED_MAIN_GROUP_ITEM)
                    lineplot_fig = self.get_line_scatter_plot(
                        collection, SELECTED_MAIN_GROUP_ITEM
                    )
                else:
                    pointplot_fig = None
                    lineplot_fig = self.get_line_scatter_plot(collection)
                return (pointplot_fig, lineplot_fig)

            @app.callback(
                [Output(main_group_dropdown_menu, 'label')
                    for main_group_dropdown_menu in main_group_dropdown_menus],
                [Input(main_group_value_id, 'n_clicks_timestamp')
                     for main_group_value_id in main_group_drop_options],
                prevent_initial_call=True
            )
            def update_main_group_labels(*timestamps):
                if not any(timestamps):
                    return dash.no_update
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                collection = self.feature_handler.get_selected_collection()
                selected_main_group_dropdown_id = \
                    MAINGROUP_DROPDOWN_TEMPLATE.format(collection)
                main_group_id = \
                    list(self.main_group_drop_options.keys())[latest_timestamp_index]

                global SELECTED_MAIN_GROUP_ITEM
                SELECTED_MAIN_GROUP_ITEM = \
                    self.main_group_drop_options[main_group_id].children

                results = []
                for main_group_dropdown_menu_id, main_group_dropdown_menu \
                        in self.main_group_dropdown_menus.items():
                    if main_group_dropdown_menu_id == selected_main_group_dropdown_id:
                        results.append(SELECTED_MAIN_GROUP_ITEM)
                    else:
                        results.append('')
                return tuple(results)

            style_outputs = [Output(main_group_dropdown_menu, 'style')
                for main_group_dropdown_menu in main_group_dropdown_menus]
            label_outputs = [
                Output(main_group_dropdown_menu, 'label', allow_duplicate=True)
                for main_group_dropdown_menu in main_group_dropdown_menus]
            outputs = style_outputs + label_outputs

            @app.callback(
                outputs,
                [Input(collection_id, 'n_clicks_timestamp')
                    for collection_id in collection_ids],
                prevent_initial_call=True
            )
            def update_selected_main_group_dropdown_styles(*timestamps):
                if not any(timestamps):
                    return dash.no_update
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))
                collection = collections[latest_timestamp_index]
                _, main_group_values = self._get_group_and_main_group_values(collection)
                selected_main_group_dropdown_id = \
                    MAINGROUP_DROPDOWN_TEMPLATE.format(collection)
                results = []
                for main_group_dropdown_menu_id, main_group_dropdown_menu \
                        in self.main_group_dropdown_menus.items():
                    if main_group_dropdown_menu_id == selected_main_group_dropdown_id:
                        results.append({'display': 'block'})
                    else:
                        results.append({'display': 'none'})
                for main_group_dropdown_menu_id, main_group_dropdown_menu \
                        in self.main_group_dropdown_menus.items():
                    if main_group_dropdown_menu_id == selected_main_group_dropdown_id:
                        results.append(main_group_values[0])
                    else:
                        results.append('')
                return tuple(results)

        @app.callback(
            [Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
             Output(SCATTER_PLOT_LINE_ID, 'figure', allow_duplicate=True)],
            [Input(collection_id, 'n_clicks_timestamp')
                for collection_id in collection_ids],
            prevent_initial_call=True
        )
        def update_plots_after_collection_change(*timestamps):
            if not any(timestamps):  # Check if any timestamp is not None
                return dash.no_update
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None))
            collection = collections[latest_timestamp_index]

            group_values, main_group_values = \
                self._get_group_and_main_group_values(collection)

            global SELECTED_MAIN_GROUP_ITEM
            if main_group_values is not None:
                SELECTED_MAIN_GROUP_ITEM = main_group_values[0]

            variables = self.feature_handler.get_variables(collection)
            if len(variables) > 1:
                pointplot_fig = self.get_point_scatter_plot(
                    collection, group_values[0], SELECTED_MAIN_GROUP_ITEM)
                lineplot_fig = self.get_line_scatter_plot(
                    collection, SELECTED_MAIN_GROUP_ITEM
                )
            else:
                pointplot_fig = None
                lineplot_fig = self.get_line_scatter_plot(collection)
            return (pointplot_fig, lineplot_fig)

        @app.callback(
            Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
            [Input(group_value_id, 'n_clicks_timestamp')
                for group_value_id in group_drop_options],
            prevent_initial_call=True
        )
        def update_point_plot_after_group_change(*timestamps):
            if not any(timestamps):
                return dash.no_update
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None))
            group_drop_option_key = \
                list(self.group_drop_options.keys())[latest_timestamp_index]
            selected_group = self.group_drop_options[group_drop_option_key].children

            collection = self.feature_handler.get_selected_collection()
            variables = self.feature_handler.get_variables(collection)
            if len(variables) > 1:
                return self.get_point_scatter_plot(
                    collection, selected_group, SELECTED_MAIN_GROUP_ITEM
                )
            else:
                return None

        @app.callback(
            [Output(group_dropdown_menu, 'label')
                for group_dropdown_menu in group_dropdown_menus],
            [Input(group_value_id, 'n_clicks_timestamp')
                 for group_value_id in group_drop_options],
            prevent_initial_call=True
        )
        def update_group_labels(*timestamps):
            if not any(timestamps):
                return dash.no_update
            collection = self.feature_handler.get_selected_collection()
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None))
            selected_group_dropdown_id = \
                list(self.group_drop_options.keys())[latest_timestamp_index]
            selected_group_item = \
                self.group_drop_options[selected_group_dropdown_id].children
            relevant_group_dropdown_id = \
                GROUP_DROPDOWN_TEMPLATE.format(collection, SELECTED_MAIN_GROUP_ITEM)
            results = []
            for group_dropdown_menu_id, group_dropdown_menu \
                    in self.group_dropdown_menus.items():
                if group_dropdown_menu_id == relevant_group_dropdown_id:
                    results.append(selected_group_item)
                else:
                    results.append('')
            return tuple(results)

        group_style_outputs = [Output(group_dropdown_menu,
                                      'style',
                                      allow_duplicate=True)
            for group_dropdown_menu in group_dropdown_menus]

        label_outputs = [
            Output(group_dropdown_menu, 'label', allow_duplicate=True)
                for group_dropdown_menu in group_dropdown_menus]

        group_outputs = group_style_outputs + label_outputs

        @app.callback(
            group_outputs,
            [Input(collection_id, 'n_clicks_timestamp')
                for collection_id in collection_ids],
            prevent_initial_call=True
        )
        def update_selected_group_dropdown_styles(*timestamps):
            if not any(timestamps):
                return dash.no_update
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None))
            collection = collections[latest_timestamp_index]
            group_values, main_group_values = \
                self._get_group_and_main_group_values(collection)

            global SELECTED_MAIN_GROUP_ITEM
            if main_group_values is not None:
                SELECTED_MAIN_GROUP_ITEM = main_group_values[0]

            selected_group_dropdown_id = GROUP_DROPDOWN_TEMPLATE.format(
                collection, SELECTED_MAIN_GROUP_ITEM
            )

            results = []
            for group_dropdown_menu_id, group_dropdown_menu \
                    in self.group_dropdown_menus.items():
                if group_dropdown_menu_id == selected_group_dropdown_id:
                    results.append({'display': 'block'})
                else:
                    results.append({'display': 'none'})
            for group_dropdown_menu_id, group_dropdown_menu \
                    in self.group_dropdown_menus.items():
                if group_dropdown_menu_id == selected_group_dropdown_id:
                    results.append(group_values[0])
                else:
                    results.append('')
            return tuple(results)

        @app.callback(
            Output(COLLAPSE, "is_open"),
            [Input(collection_id, 'n_clicks_timestamp')
                for collection_id in collection_ids]
        )
        def collapse_when_too_few_variables_in_collection(*timestamps):
            if not any(timestamps):
                return dash.no_update
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None))
            collection = collections[latest_timestamp_index]

            variables = self.feature_handler.get_variables(collection)

            return len(variables) > 1
