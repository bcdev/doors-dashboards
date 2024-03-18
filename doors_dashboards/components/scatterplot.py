from typing import Dict, List
from dash import dcc, html, Dash, Input, Output, dash, no_update, State
import plotly.express as px
from dash.development.base_component import Component
import dash_bootstrap_components as dbc

from doors_dashboards.components.constant import COLLECTION_TEMPLATE, SCATTER_FONT_SIZE, \
    FONT_SIZE_NUMBER
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

LINE_VAR_DROPDOWN_ID_TEMPLATE = \
    "line_var_drop_down_id_{0}"  # collection
POINT_X_VAR_DROPDOWN_ID_TEMPLATE = \
    "point_x_var_drop_down_id_{0}"  # collection
POINT_Y_VAR_DROPDOWN_ID_TEMPLATE = \
    "point_y_var_drop_down_id_{0}"  # collection
LINE_VAR_DROP_OPTION_TEMPLATE = \
    "line_var_drop_option_id_{0}_{1}"  # collection variable
POINT_X_VAR_DROP_OPTION_TEMPLATE = \
    "point_x_var_drop_option_id_{0}_{1}"  # collection variable
POINT_Y_VAR_DROP_OPTION_TEMPLATE = \
    "point_y_var_drop_option_id_{0}_{1}"  # collection variable

COLLAPSE = "collapse_id"

ALL_GROUP_MEMBERS = "all"
SELECTED_MAIN_GROUP_ITEM = ""
SELECTED_GROUP_ITEM = ""
SELECTED_X_VAR_ITEM = ""
SELECTED_Y_VAR_ITEM = ""


class ScatterplotComponent(DashboardComponent):

    def __init__(self):
        self.feature_handler = None
        self.group_dropdown_menus = dict()
        self.group_drop_options = dict()
        self.main_group_dropdown_menus = dict()
        self.main_group_drop_options = dict()

        self.line_dropdown_menus = dict()
        self.line_drop_options = dict()
        self.point_x_dropdown_menus = dict()
        self.point_x_drop_options = dict()
        self.point_y_dropdown_menus = dict()
        self.point_y_drop_options = dict()

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

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
                'display': 'none'
            },
            size="lg",
            color="secondary"
        )

    def _setup_variable_dropdown_menus(self):
        collections = self.feature_handler.get_collections()
        for collection in collections:
            variables = self.feature_handler.get_variables(collection)
            line_drop_menu_items = []
            point_x_drop_menu_items = []
            point_y_drop_menu_items = []
            for variable in variables:
                line_drop_option_id = LINE_VAR_DROP_OPTION_TEMPLATE.format(
                    collection, variable
                )
                point_x_drop_option_id = \
                    POINT_X_VAR_DROP_OPTION_TEMPLATE.format(
                        collection, variable
                    )
                point_y_drop_option_id = \
                    POINT_Y_VAR_DROP_OPTION_TEMPLATE.format(
                        collection, variable
                    )
                line_drop_option = dbc.DropdownMenuItem(
                    variable,
                    id=line_drop_option_id,
                    n_clicks=1,
                    style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY}
                )
                point_x_drop_option = dbc.DropdownMenuItem(
                    variable,
                    id=point_x_drop_option_id,
                    n_clicks=1,
                    style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY}
                )
                point_y_drop_option = dbc.DropdownMenuItem(
                    variable,
                    id=point_y_drop_option_id,
                    n_clicks=1,
                    style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY}
                )
                self.line_drop_options[line_drop_option_id] = line_drop_option
                self.point_x_drop_options[point_x_drop_option_id] = \
                    point_x_drop_option
                self.point_y_drop_options[point_y_drop_option_id] = \
                    point_y_drop_option
                line_drop_menu_items.append(line_drop_option)
                point_x_drop_menu_items.append(point_x_drop_option)
                point_y_drop_menu_items.append(point_y_drop_option)
            line_dropdown_id = \
                LINE_VAR_DROPDOWN_ID_TEMPLATE.format(collection)
            point_x_dropdown_id = \
                POINT_X_VAR_DROPDOWN_ID_TEMPLATE.format(collection)
            point_y_dropdown_id = \
                POINT_Y_VAR_DROPDOWN_ID_TEMPLATE.format(collection)
            self.line_dropdown_menus[line_dropdown_id] = \
                self._get_dropdown_menu(
                    line_dropdown_id,
                    line_drop_menu_items,
                    variables[0]
                )
            self.point_x_dropdown_menus[point_x_dropdown_id] = \
                self._get_dropdown_menu(
                    point_x_dropdown_id,
                    point_x_drop_menu_items,
                    variables[0]
                )
            self.point_y_dropdown_menus[point_y_dropdown_id] = \
                self._get_dropdown_menu(
                    point_y_dropdown_id,
                    point_y_drop_menu_items,
                    variables[-1]
                )

    def _setup_group_dropdown_menus(self):
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
                        n_clicks=1,
                        style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY}
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
                            n_clicks=1,
                            style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY}
                        )
                        self.group_drop_options[group_drop_option_id] = \
                            group_drop_down_menu_item
                        group_dropdown_menu_items.append(group_drop_down_menu_item)

                    group_drop_option_id = \
                        GROUP_DROP_OPTION_TEMPLATE.format(
                            collection, main_group, ALL_GROUP_MEMBERS
                        )
                    group_drop_down_menu_item = dbc.DropdownMenuItem(
                        ALL_GROUP_MEMBERS,
                        id=group_drop_option_id,
                        n_clicks=1,
                        style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY}
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
                            n_clicks=1,
                            style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY}
                        )
                    dropdown_menu_items.append(group_drop_option)
                    self.group_drop_options[group_drop_option_id] = group_drop_option

                group_drop_option_id = \
                    GROUP_DROP_OPTION_TEMPLATE.format(
                        collection, "all", ALL_GROUP_MEMBERS
                    )
                group_drop_down_menu_item = dbc.DropdownMenuItem(
                    ALL_GROUP_MEMBERS,
                    id=group_drop_option_id,
                    n_clicks=1,
                    style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY}
                )
                self.group_drop_options[group_drop_option_id] = \
                    group_drop_down_menu_item
                dropdown_menu_items.append(group_drop_down_menu_item)

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
        self._setup_group_dropdown_menus()
        self._setup_variable_dropdown_menus()
        collection = self.feature_handler.get_selected_collection()
        # For rendering scatterplots
        pointplot_fig = self.get_point_scatter_plot(collection)
        lineplot_fig = self.get_line_scatter_plot(collection)

        # SELECTED_MAIN_GROUP_ITEM = "all"
        main_group_drop_down_menus = \
            list(self.main_group_dropdown_menus.values())
        if len(main_group_drop_down_menus) > 0:
            main_group_drop_down_menus[0].style['display'] = 'block'
            main_group_drop_options = list(self.main_group_drop_options.values())
            # SELECTED_MAIN_GROUP_ITEM = main_group_drop_options[0].children

        line_drop_down_menus = list(self.line_dropdown_menus.values())
        line_drop_down_menus[0].style['display'] = 'block'

        upper_row = dbc.Row([
            dbc.Label('Cruise', style={'color': FONT_COLOR,
                                       'fontFamily': FONT_FAMILY,
                                       'fontSize': 'larger',
                                       'padding': '10px 0 0 12px',
                                       },
                      className="col-sm-1 col-md-1"),
            dbc.Col(
                main_group_drop_down_menus,
                className="col-sm-3 col-md-3",
                style={'padding-left': '0px'}
            ),
            dbc.Label('Variable', style={'color': FONT_COLOR,
                                         'fontFamily': FONT_FAMILY,
                                         'fontSize': 'larger',
                                         'paddingTop': '10px',
                                         },
                      className="col-sm-1 col-md-1"),
            dbc.Col(
                line_drop_down_menus,
                className="col-sm-3 col-md-4"
            )
        ]
        )
        upper_components = [
            upper_row,
            dcc.Graph(
                id=SCATTER_PLOT_LINE_ID, figure=lineplot_fig, style=DISPLAY_STYLE
            )
        ]
        group_drop_down_menus = list(self.group_dropdown_menus.values())
        group_drop_down_menus[0].style['display'] = 'block'
        group_drop_down_options = list(self.group_drop_options.values())
        # global SELECTED_GROUP_ITEM
        # SELECTED_GROUP_ITEM = group_drop_down_options[0].children
        point_x_drop_down_menus = list(self.point_x_dropdown_menus.values())
        point_x_drop_down_menus[0].style['display'] = 'block'
        point_x_drop_options = list(self.point_x_drop_options.values())
        # global SELECTED_X_VAR_ITEM
        # SELECTED_X_VAR_ITEM = point_x_drop_options[0].children
        point_y_drop_down_menus = list(self.point_y_dropdown_menus.values())
        point_y_drop_down_menus[0].style['display'] = 'block'
        point_y_drop_options = list(self.point_y_drop_options.values())
        # global SELECTED_Y_VAR_ITEM
        # SELECTED_Y_VAR_ITEM = point_y_drop_options[0].children

        lower_row = dbc.Row([

            dbc.Label('Station', style={'color': FONT_COLOR,
                                        'fontFamily': FONT_FAMILY,
                                        'fontSize': 'larger',
                                        'paddingTop': '10px',
                                        },
                      className="col-sm-1"),
            dbc.Col(
                group_drop_down_menus,
                className="col-sm-2",
                style={'paddingLeft': '3px'}
            ),
            dbc.Label('X Variable', style={'color': FONT_COLOR,
                                           'fontFamily': FONT_FAMILY,
                                           'fontSize': 'larger',
                                           'paddingTop': '10px',
                                           'text-wrap': 'nowrap',
                                           'paddingLeft': '59px'},
                      className="col-sm-2"),
            dbc.Col(
                point_x_drop_down_menus,
                className="col-sm-2",
                style={'padding-left': '1px'}
            ),
            dbc.Label('Y Variable', style={'color': FONT_COLOR,
                                           'fontFamily': FONT_FAMILY,
                                           'fontSize': 'larger',
                                           'paddingTop': '10px',
                                           'text-wrap': 'nowrap',
                                           'paddingLeft': '68px'},
                      className="col-sm-2"),
            dbc.Col(
                point_y_drop_down_menus,
                className="col-sm-3"
            )
        ]
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
                               selected_main_group_item: str = "",
                               x_variable: str = None,
                               y_variable: str = None,
                               ):
        df = self.get_dataframe(
            collection, selected_group_item, selected_main_group_item
        )
        levels = self.feature_handler.get_levels(collection)
        variables = self.feature_handler.get_variables(collection)
        if len(variables) > 1:
            if x_variable is None:
                x_variable = variables[0]
            if y_variable is None:
                y_variable = variables[-1]
            fig = px.scatter(
                df,
                x=x_variable,
                y=y_variable,
                color=levels[-1],
                color_discrete_sequence=px.colors.qualitative.Set1,
            )
            fig.update_layout(
                font=dict(family=FONT_FAMILY, size=18, color=FONT_COLOR),
                plot_bgcolor="rgb(0,0,0,0)",
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    title=dict(
                        text=levels[-1].title(),
                        font=dict(
                            family="Roboto, Helvetica, Arial, sans-serif",
                            size=18,
                            color=FONT_COLOR
                        ),
                        # orientation="v",
                    ),
                )
            )
            fig.update_traces(marker_size=10)
            fig.update_xaxes(title_text=x_variable.title())
            fig.update_yaxes(title_text=y_variable.title())
            return fig

    def get_line_scatter_plot(self,
                              collection: str,
                              selected_main_group_item: str = "",
                              variable: str = None):
        df = self.get_dataframe(
            collection, ALL_GROUP_MEMBERS, selected_main_group_item
        )
        df = df.sort_values(by='sampling depth [m]')
        levels = self.feature_handler.get_levels(collection)
        if variable is None:
            variable = self.feature_handler.get_variables(collection)[0]
        fig = px.line(
            df,
            x=variable,
            y=levels[-1],
            color=levels[-2],
            line_shape='spline', render_mode='svg',
            markers=True
        )
        fig.update_yaxes(autorange='reversed')
        fig.update_xaxes(title_text=variable.title())
        fig.update_yaxes(title_text='Sampling Depth [m]')
        fig.update_layout(
            font=dict(family=FONT_FAMILY, size=18,
                      color=FONT_COLOR))
        fig.update_traces(marker=dict(size=10, color='yellow', symbol='circle'))
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

        line_dropdown_menus = list(self.line_dropdown_menus.keys())
        line_drop_options = list(self.line_drop_options.keys())

        point_x_dropdown_menus = list(self.point_x_dropdown_menus.keys())
        point_x_drop_options = list(self.point_x_drop_options.keys())

        point_y_dropdown_menus = list(self.point_y_dropdown_menus.keys())
        point_y_drop_options = list(self.point_y_drop_options.keys())

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

                # global SELECTED_MAIN_GROUP_ITEM
                # SELECTED_MAIN_GROUP_ITEM = \
                #  self.main_group_drop_options[main_group_id].children

                group_values = self._get_group_values_for_main_group(
                    collection, self.main_group_drop_options[main_group_id].children
                )

                valid_group_id = \
                    GROUP_DROPDOWN_TEMPLATE.format(collection,
                                                   self.main_group_drop_options[
                                                       main_group_id].children)

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
                 Output(SCATTER_PLOT_LINE_ID, 'figure', allow_duplicate=True),
                 Output("group_selector", 'data')],
                [Input(main_group_value_id, 'n_clicks_timestamp')
                 for main_group_value_id in main_group_drop_options],
                prevent_initial_call=True
            )
            def update_plots_and_group_store_after_main_group_change(*timestamps):
                collection = self.feature_handler.get_selected_collection()
                if not any(timestamps):  # Check if any timestamp is not None
                    return dash.no_update
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None))

                main_group_id = \
                    list(self.main_group_drop_options.keys())[latest_timestamp_index]

                selected_main_group_item = \
                    self.main_group_drop_options[main_group_id].children

                group_values = self._get_group_values_for_main_group(
                    collection, selected_main_group_item
                )
                group_selector = {
                    "main_group": selected_main_group_item,
                    "group_values": group_values[0]
                }

                variables = self.feature_handler.get_variables(collection)
                if len(variables) > 1:
                    pointplot_fig = self.get_point_scatter_plot(
                        collection, group_values[0], selected_main_group_item)
                    lineplot_fig = self.get_line_scatter_plot(
                        collection, selected_main_group_item
                    )
                else:
                    pointplot_fig = None
                    lineplot_fig = self.get_line_scatter_plot(collection)
                return pointplot_fig, lineplot_fig, group_selector

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
                selected_main_group_item = \
                    self.main_group_drop_options[main_group_id].children

                results = []
                for main_group_dropdown_menu_id, main_group_dropdown_menu \
                        in self.main_group_dropdown_menus.items():
                    if main_group_dropdown_menu_id == selected_main_group_dropdown_id:
                        results.append(selected_main_group_item)
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
                [Input('collection_selector', 'data')],
                prevent_initial_call=True
            )
            def update_selected_main_group_dropdown_styles(data):
                if data is None:
                    return dash.no_update
                selected_collection = data.get("collection")
                _, main_group_values = (
                    self._get_group_and_main_group_values(selected_collection))
                selected_main_group_dropdown_id = \
                    MAINGROUP_DROPDOWN_TEMPLATE.format(selected_collection)
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
            [Input("general", "data")],
            prevent_initial_call=True
        )
        def update_plots_after_general_store_update(general_data):
            if general_data is None or "collection" not in general_data:
                return no_update
            selected_collection = general_data["collection"]
            if "groups" in general_data:
                groups = general_data.get("groups", {}).get(selected_collection)
            if "variable" in general_data:
                line_var = general_data.get("variable", {}).get(selected_collection)
                if len(groups) > 0:
                    variables = self.feature_handler.get_variables(selected_collection)
                    if len(variables) > 1:
                        pointplot_fig = self.get_point_scatter_plot(
                            selected_collection, groups[1], groups[0],
                            variables[0], variables[-1]
                        )
                        lineplot_fig = self.get_line_scatter_plot(
                            selected_collection, groups[0], line_var
                        )
                    else:
                        pointplot_fig = None
                        lineplot_fig = self.get_line_scatter_plot(selected_collection)
                    return pointplot_fig, lineplot_fig

        @app.callback(
            Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
            [Input('group_selector', 'data')],
            prevent_initial_call=True
        )
        def update_point_plot_after_group_change(selected_group_data):
            if selected_group_data is None:
                return dash.no_update
            group_item = selected_group_data["group_values"]

            collection = self.feature_handler.get_selected_collection()
            variables = self.feature_handler.get_variables(collection)
            if len(variables) > 1:
                return self.get_point_scatter_plot(
                    collection, group_item, selected_group_data["main_group"],
                    variables[0], variables[-1]
                )
            else:
                return None

        @app.callback(
            [[Output(group_dropdown_menu, 'label')
              for group_dropdown_menu in group_dropdown_menus],
             Output("group_selector", "data",
                    allow_duplicate=True)],
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
            _, main_group_values = self._get_group_and_main_group_values(collection)
            relevant_group_dropdown_id = GROUP_DROPDOWN_TEMPLATE.format(
                collection, main_group_values[0]
            )
            selected_group = {
                "main_group": main_group_values[0],
                "group_values": selected_group_item
            }
            results = []
            for group_dropdown_menu_id, group_dropdown_menu \
                    in self.group_dropdown_menus.items():
                if group_dropdown_menu_id == relevant_group_dropdown_id:
                    results.append(selected_group_item)
                else:
                    results.append('')
            return tuple(results), selected_group

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
            [Input("collection_selector", 'data')],
            prevent_initial_call=True
        )
        def update_selected_group_dropdown_styles(selected_data):
            if not selected_data:
                return dash.no_update

            collection = selected_data["collection"]
            group_values, main_group_values = \
                self._get_group_and_main_group_values(collection)

            if main_group_values is not None:
                selected_group_dropdown_id = GROUP_DROPDOWN_TEMPLATE.format(
                    collection, main_group_values[0]
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
            [Input("collection_selector", 'data')]
        )
        def collapse_when_too_few_variables_in_collection(selected_data):
            if not selected_data:
                return dash.no_update
            collection = selected_data["collection"]
            variables = self.feature_handler.get_variables(collection)

            return len(variables) > 1

        @app.callback(
            [[Output(line_dropdown_menu, 'label')
              for line_dropdown_menu in line_dropdown_menus],
             Output("variable_selector", "data", allow_duplicate=True)],
            [Input(line_drop_id, 'n_clicks_timestamp')
             for line_drop_id in line_drop_options],
            prevent_initial_call=True
        )
        def update_line_var_dropdown_after_click(*timestamps):
            if not any(timestamps):
                return dash.no_update
            collection = self.feature_handler.get_selected_collection()
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None))

            line_drop_option_id = \
                list(self.line_drop_options.keys())[latest_timestamp_index]
            line_drop_option_value = \
                self.line_drop_options[line_drop_option_id].children
            relevant_line_dropdown_menu_id = \
                LINE_VAR_DROPDOWN_ID_TEMPLATE.format(collection)
            results = []
            for line_dropdown_menu_id, line_dropdown_menu \
                    in self.line_dropdown_menus.items():
                if line_dropdown_menu_id == relevant_line_dropdown_menu_id:
                    results.append(line_drop_option_value)
                else:
                    results.append('')
            variable_selector = {
                "line_variable": line_drop_option_value
            }
            return tuple(results), variable_selector

        @app.callback(
            [[Output(point_x_dropdown_menu, 'label')
              for point_x_dropdown_menu in point_x_dropdown_menus], Output(
                'variable_selector', 'data',
                allow_duplicate=True)],
            [Input(point_x_drop_id, 'n_clicks_timestamp')
             for point_x_drop_id in point_x_drop_options],
            prevent_initial_call=True
        )
        def update_point_x_var_dropdown_after_click(*timestamps):
            if not any(timestamps):
                return dash.no_update
            collection = self.feature_handler.get_selected_collection()
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None))

            point_x_drop_option_id = \
                list(self.point_x_drop_options.keys())[latest_timestamp_index]
            point_x_drop_option_value = \
                self.point_x_drop_options[point_x_drop_option_id].children
            variable_selector = {
                'x_variable': point_x_drop_option_value
            }
            relevant_point_x_dropdown_menu_id = \
                POINT_X_VAR_DROPDOWN_ID_TEMPLATE.format(collection)
            results = []
            for point_x_dropdown_menu_id, point_x_dropdown_menu \
                    in self.point_x_dropdown_menus.items():
                if point_x_dropdown_menu_id == relevant_point_x_dropdown_menu_id:
                    results.append(point_x_drop_option_value)
                else:
                    results.append('')
            return tuple(results), variable_selector

        @app.callback(
            [[Output(point_y_dropdown_menu, 'label')
              for point_y_dropdown_menu in point_y_dropdown_menus], Output(
                'variable_selector', 'data',
                allow_duplicate=True)],
            [Input(point_y_drop_id, 'n_clicks_timestamp')
             for point_y_drop_id in point_y_drop_options],
            prevent_initial_call=True
        )
        def update_point_y_var_dropdown_after_click(*timestamps):
            if not any(timestamps):
                return dash.no_update
            collection = self.feature_handler.get_selected_collection()
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None))

            point_y_drop_option_id = \
                list(self.point_y_drop_options.keys())[latest_timestamp_index]
            point_y_drop_option_value = \
                self.point_y_drop_options[point_y_drop_option_id].children

            variable_selector = {
                'y_variable': point_y_drop_option_value
            }
            relevant_point_y_dropdown_menu_id = \
                POINT_Y_VAR_DROPDOWN_ID_TEMPLATE.format(collection)
            results = []
            for point_y_dropdown_menu_id, point_y_dropdown_menu \
                    in self.point_y_dropdown_menus.items():
                if point_y_dropdown_menu_id == relevant_point_y_dropdown_menu_id:
                    results.append(point_y_drop_option_value)
                else:
                    results.append('')
            return tuple(results), variable_selector

        line_style_outputs = [Output(line_dropdown_menu,
                                     'style',
                                     allow_duplicate=True)
                              for line_dropdown_menu in line_dropdown_menus]

        line_label_outputs = [
            Output(line_dropdown_menu, 'label', allow_duplicate=True)
            for line_dropdown_menu in line_dropdown_menus]

        line_outputs = line_style_outputs + line_label_outputs

        @app.callback(
            line_outputs,
            [Input('general', 'data')],
            prevent_initial_call=True
        )
        def update_line_var_dropdown_after_collection_change(selected_data):
            if selected_data is None or "collection" not in selected_data:
                return no_update
            collection = selected_data["collection"]
            variable = self.feature_handler.get_variables(collection)[0]

            selected_line_dropdown_id = \
                LINE_VAR_DROPDOWN_ID_TEMPLATE.format(collection)

            results = []
            for line_dropdown_menu_id, line_dropdown_menu \
                    in self.line_dropdown_menus.items():
                if line_dropdown_menu_id == selected_line_dropdown_id:
                    results.append({'display': 'block'})
                else:
                    results.append({'display': 'none'})
            for line_dropdown_menu_id, line_dropdown_menu \
                    in self.line_dropdown_menus.items():
                if line_dropdown_menu_id == selected_line_dropdown_id:
                    results.append(variable)
                else:
                    results.append('')
            return tuple(results)

        point_x_style_outputs = [Output(point_x_dropdown_menu,
                                        'style',
                                        allow_duplicate=True)
                                 for point_x_dropdown_menu in point_x_dropdown_menus]

        point_x_label_outputs = [
            Output(point_x_dropdown_menu, 'label', allow_duplicate=True)
            for point_x_dropdown_menu in point_x_dropdown_menus]

        point_x_outputs = point_x_style_outputs + point_x_label_outputs

        @app.callback(
            point_x_outputs,
            [Input('collection_selector', 'data')],
            prevent_initial_call=True
        )
        def update_point_x_var_dropdown_after_collection_change(selected_data):
            if selected_data is None:
                return dash.no_update
            collection = selected_data["collection"]
            variable = self.feature_handler.get_variables(collection)[0]

            selected_point_x_dropdown_id = \
                POINT_X_VAR_DROPDOWN_ID_TEMPLATE.format(collection)

            results = []
            for point_x_dropdown_menu_id, point_x_dropdown_menu \
                    in self.point_x_dropdown_menus.items():
                if point_x_dropdown_menu_id == selected_point_x_dropdown_id:
                    results.append({'display': 'block'})
                else:
                    results.append({'display': 'none'})
            for point_x_dropdown_menu_id, point_x_dropdown_menu \
                    in self.point_x_dropdown_menus.items():
                if point_x_dropdown_menu_id == selected_point_x_dropdown_id:
                    results.append(variable)
                else:
                    results.append('')
            return tuple(results)

        point_y_style_outputs = [Output(point_y_dropdown_menu,
                                        'style',
                                        allow_duplicate=True)
                                 for point_y_dropdown_menu in point_y_dropdown_menus]

        point_y_label_outputs = [
            Output(point_y_dropdown_menu, 'label', allow_duplicate=True)
            for point_y_dropdown_menu in point_y_dropdown_menus]

        point_y_outputs = point_y_style_outputs + point_y_label_outputs

        @app.callback(
            point_y_outputs,
            [Input('collection_selector', 'data')],
            prevent_initial_call=True
        )
        def update_point_y_var_dropdown_after_collection_change(selected_data):
            if selected_data is None:
                return dash.no_update
            collection = selected_data["collection"]
            variable = self.feature_handler.get_variables(collection)[-1]

            selected_point_y_dropdown_id = \
                POINT_Y_VAR_DROPDOWN_ID_TEMPLATE.format(collection)

            results = []
            for point_y_dropdown_menu_id, point_y_dropdown_menu \
                    in self.point_y_dropdown_menus.items():
                if point_y_dropdown_menu_id == selected_point_y_dropdown_id:
                    results.append({'display': 'block'})
                else:
                    results.append({'display': 'none'})
            for point_y_dropdown_menu_id, point_y_dropdown_menu \
                    in self.point_y_dropdown_menus.items():
                if point_y_dropdown_menu_id == selected_point_y_dropdown_id:
                    results.append(variable)
                else:
                    results.append('')
            return tuple(results)

        @app.callback(
            Output(SCATTER_PLOT_LINE_ID, 'figure', allow_duplicate=True),
            [Input("variable_selector", 'data'),
             Input("group_selector", 'data')],
            prevent_initial_call=True
        )
        def update_line_plot_after_line_var_change(selected_variable_data,
                                                   selected_group_data):
            if (selected_variable_data is None or "line_variable" not in
                    selected_variable_data):
                return dash.no_update
            if "main_group" in selected_group_data:
                selected_main_group_item = selected_group_data["main_group"]
            else:
                _, selected_main_group_item = self._get_group_and_main_group_values(
                    self.feature_handler.get_selected_collection)
            variable = selected_variable_data["line_variable"]
            return self.get_line_scatter_plot(
                collection, selected_main_group_item, variable
            )

        @app.callback(
            Output(SCATTER_PLOT_ID, 'figure', allow_duplicate=True),
            [Input('variable_selector', 'data')],
            prevent_initial_call=True
        )
        def update_point_plot_after_point_x_or_y_var_change(variable_data):
            if variable_data is None:
                return no_update

            selected_collection = self.feature_handler.get_selected_collection()
            variables = self.feature_handler.get_variables(selected_collection)

            group_values, main_group_values = \
                self._get_group_and_main_group_values(selected_collection)
            if "y_variable" in variable_data:
                y_variable = variable_data["y_variable"]
                x_variable = variables[0]

                return self.get_point_scatter_plot(
                    collection, group_values[0], main_group_values[0],
                    x_variable, y_variable
                )
            elif "x_variable" in variable_data:
                x_variable = variable_data["x_variable"]
                y_variable = variables[-1]

                return self.get_point_scatter_plot(
                    collection, group_values[0], main_group_values[0],
                    x_variable, y_variable
                )

        @app.callback(
            [Output('group_selector', 'data',
                    allow_duplicate=True),
             Output('variable_selector', 'data',
                    allow_duplicate=True)
             ],
            [Input("general", 'data')],
            prevent_initial_call=True
        )
        def update_group_selector_and_variable_selector_when_collection_selector_updates(
                selected_data):
            if selected_data is None or "collection" not in selected_data:
                return no_update
            if "collection" in selected_data:
                selected_collection = selected_data["collection"]
                x_variable = self.feature_handler.get_variables(selected_collection)[0]
                y_variable = self.feature_handler.get_variables(selected_collection)[-1]
                if "variable" in selected_data:
                    line_var = selected_data.get("variable", {}).get(
                        selected_collection)
                    variable_selector = {
                        'x_variable': x_variable,
                        'y_variable': y_variable,
                        'line_variable': line_var
                    }
                else:
                    variable_selector = {
                        'x_variable': x_variable,
                        'y_variable': y_variable,
                    }
                if "groups" in selected_data:
                    groups = selected_data.get("groups", {}).get(selected_collection)
                    main_group_value = groups[0]
                    group_value = groups[1]
                    group_selector = {
                        "main_group": main_group_value,
                        "group_values": group_value,
                    }
                else:
                    group_values, main_group_values = \
                        self._get_group_and_main_group_values(selected_collection)
                    group_selector = {
                        "main_group": main_group_values[0],
                        "group_values": group_values[0],
                    }
                return group_selector, variable_selector

        @app.callback(
            [Output("general", 'data')],
            [Input('group_selector', 'data'),
             Input('variable_selector', 'data')
             ],
            State("general", "data"),
            prevent_initial_call=True
        )
        def update_general_store_when_group_variable_updates(selected_group_data,
                                                             selected_variable_data,
                                                             general_data):
            general_data = general_data or {}
            if "collection" not in general_data:
                general_data["collection"] = (
                    self.feature_handler.get_selected_collection())
            if "groups" not in general_data:
                general_data["variables"] = {}
            if "variables" not in general_data:
                general_data["variables"] = {}
            if "main_group" in selected_group_data:
                selected_main_group = {
                    "main_group": selected_group_data["main_group"]
                }
                collection = general_data["collection"]
                general_data["groups"][collection] = selected_main_group
            if "group_values" in selected_group_data:
                selected_group_item = selected_group_data["group_values"]
            if "x_variable" in selected_variable_data:
                x_variable = selected_variable_data["x_variable"]
            if "y_variable" in selected_variable_data:
                y_variable = selected_variable_data["y_variable"]
            if "line_variable" in selected_variable_data:
                line_variable = selected_variable_data["y_variable"]
            return general_data
