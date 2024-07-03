from dash import callback
from dash import dash
from dash import dcc
from dash import html
from dash import Input
from dash import no_update
from dash import Output
from dash import State
from dash.development.base_component import Component
import dash_bootstrap_components as dbc
import plotly.express as px
from typing import Dict
from typing import List
from typing import Tuple

from doors_dashboards.components.constant import (
    COLLECTION,
    FONT_FAMILY,
    FONT_COLOR,
    SCATTER_PLOT_LINE_ID,
    PLOT_BGCOLOR,
    SCATTER_PLOT_ID,
    MAIN_GROUP,
    GROUP,
    GENERAL_STORE_ID,
    GROUPS_SECTION,
)
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

DISPLAY_STYLE = {"height": "35vh"}
GROUP_DROP_OPTION_TEMPLATE = "group_drp_option_{0}_{1}_{2}"
MAIN_GROUP_DROP_OPTION_TEMPLATE = "main_group_drp_option_{0}_{1}"
GROUP_DROPDOWN_TEMPLATE = "group_drp_option_{0}_{1}"
MAIN_GROUP_DROPDOWN_TEMPLATE = "main_group_drp_option_{0}"
MAIN_GROUP_DROPDOWN_OFFSET = MAIN_GROUP_DROPDOWN_TEMPLATE.index("{")

LINE_VAR_DROPDOWN_ID_TEMPLATE = "line_var_drop_down_id_{0}"  # collection
LINE_VAR_DROPDOWN_OFFSET = LINE_VAR_DROPDOWN_ID_TEMPLATE.index("{")
POINT_X_VAR_DROPDOWN_ID_TEMPLATE = "point_x_var_drop_down_id_{0}"  # collection
POINT_X_VAR_DROPDOWN_OFFSET = POINT_X_VAR_DROPDOWN_ID_TEMPLATE.index("{")
POINT_Y_VAR_DROPDOWN_ID_TEMPLATE = "point_y_var_drop_down_id_{0}"  # collection
POINT_Y_VAR_DROPDOWN_OFFSET = POINT_Y_VAR_DROPDOWN_ID_TEMPLATE.index("{")
LINE_VAR_DROP_OPTION_TEMPLATE = "line_var_drop_option_id_{0}_{1}"  # collection variable
POINT_X_VAR_DROP_OPTION_TEMPLATE = (
    "point_x_var_drop_option_id_{0}_{1}"  # collection variable
)
POINT_Y_VAR_DROP_OPTION_TEMPLATE = (
    "point_y_var_drop_option_id_{0}_{1}"  # collection variable
)

ALL_GROUP_MEMBERS = "all"
COLLAPSE = "collapse_id"
COMPONENT_STORE_ID = "scatterplot_component_store"
LINE_VARIABLE = "line_variable"
TEMP_STORE_ID = "scatterplot_temp_store"
VARIABLES_SECTION = "variables"
X_VARIABLE = "x_variable"
Y_VARIABLE = "y_variable"


class ScatterplotComponent(DashboardComponent):

    def __init__(self, dashboard_id: str = None):
        self.feature_handler = None
        self.group_dropdown_menus = dict()
        self.group_drop_options = dict()
        self.main_group_dropdown_menus = dict()
        self.main_group_drop_options = dict()

        self.line_dropdown_menus = dict()
        self.xvar_drop_options = dict()
        self.point_x_dropdown_menus = dict()
        self.point_x_drop_options = dict()
        self.point_y_dropdown_menus = dict()
        self.point_y_drop_options = dict()
        self._encodings = dict()
        self._dashboard_id = dashboard_id

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
            style={"fontFamily": FONT_FAMILY, "display": "none"},
            color="secondary",
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
                point_x_drop_option_id = POINT_X_VAR_DROP_OPTION_TEMPLATE.format(
                    collection, variable
                )
                point_y_drop_option_id = POINT_Y_VAR_DROP_OPTION_TEMPLATE.format(
                    collection, variable
                )
                line_drop_option = dbc.DropdownMenuItem(
                    variable,
                    id=line_drop_option_id,
                    n_clicks=1,
                    style={"fontSize": "larger", "fontfamily": FONT_FAMILY},
                )
                point_x_drop_option = dbc.DropdownMenuItem(
                    variable,
                    id=point_x_drop_option_id,
                    n_clicks=1,
                    style={"fontSize": "larger", "fontfamily": FONT_FAMILY},
                )
                point_y_drop_option = dbc.DropdownMenuItem(
                    variable,
                    id=point_y_drop_option_id,
                    n_clicks=1,
                    style={"fontSize": "larger", "fontfamily": FONT_FAMILY},
                )
                self.xvar_drop_options[line_drop_option_id] = line_drop_option
                self.point_x_drop_options[point_x_drop_option_id] = point_x_drop_option
                self.point_y_drop_options[point_y_drop_option_id] = point_y_drop_option
                line_drop_menu_items.append(line_drop_option)
                point_x_drop_menu_items.append(point_x_drop_option)
                point_y_drop_menu_items.append(point_y_drop_option)
            line_dropdown_id = self.encode_linevar_dropdown(collection)
            point_x_dropdown_id = self.encode_xvar_dropdown(collection)
            point_y_dropdown_id = self.encode_yvar_dropdown(collection)
            self.line_dropdown_menus[line_dropdown_id] = self._get_dropdown_menu(
                line_dropdown_id, line_drop_menu_items, variables[0]
            )
            self.point_x_dropdown_menus[point_x_dropdown_id] = self._get_dropdown_menu(
                point_x_dropdown_id, point_x_drop_menu_items, variables[0]
            )
            self.point_y_dropdown_menus[point_y_dropdown_id] = self._get_dropdown_menu(
                point_y_dropdown_id, point_y_drop_menu_items, variables[-1]
            )

    def _setup_group_dropdown_menus(self):
        collections = self.feature_handler.get_collections()
        for collection in collections:
            group_values, main_group_values = self._get_group_and_main_group_values(
                collection
            )
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
                        style={"fontSize": "larger", "fontFamily": FONT_FAMILY},
                    )
                    self.main_group_drop_options[main_group_drop_option_id] = (
                        main_group_drop_option
                    )
                    dropdown_main_menu_items.append(main_group_drop_option)
                    # set up group drop options
                    groups = self._get_group_values_for_main_group(
                        collection, main_group
                    )
                    group_dropdown_menu_items = []
                    for member in groups:
                        group_drop_option_id = GROUP_DROP_OPTION_TEMPLATE.format(
                            collection, main_group, member
                        )
                        group_drop_down_menu_item = dbc.DropdownMenuItem(
                            member,
                            id=group_drop_option_id,
                            n_clicks=1,
                            style={"fontSize": "larger", "fontFamily": FONT_FAMILY},
                        )
                        self.group_drop_options[group_drop_option_id] = (
                            group_drop_down_menu_item
                        )
                        group_dropdown_menu_items.append(group_drop_down_menu_item)

                    group_drop_option_id = GROUP_DROP_OPTION_TEMPLATE.format(
                        collection, main_group, ALL_GROUP_MEMBERS
                    )
                    group_drop_down_menu_item = dbc.DropdownMenuItem(
                        ALL_GROUP_MEMBERS,
                        id=group_drop_option_id,
                        n_clicks=1,
                        style={"fontSize": "larger", "fontFamily": FONT_FAMILY},
                    )
                    self.group_drop_options[group_drop_option_id] = (
                        group_drop_down_menu_item
                    )
                    group_dropdown_menu_items.append(group_drop_down_menu_item)

                    group_dropdown_id = self.encode_group_dropdown(
                        collection, main_group
                    )
                    self.group_dropdown_menus[group_dropdown_id] = (
                        self._get_dropdown_menu(
                            group_dropdown_id, group_dropdown_menu_items, groups[0]
                        )
                    )
                main_group_dropdown_id = self.encode_main_group_dropdown(collection)
                self.main_group_dropdown_menus[main_group_dropdown_id] = (
                    self._get_dropdown_menu(
                        main_group_dropdown_id,
                        dropdown_main_menu_items,
                        main_group_values[0],
                    )
                )
            else:
                dropdown_menu_items = []
                for member in group_values:
                    group_drop_option_id = GROUP_DROP_OPTION_TEMPLATE.format(
                        collection, "all", member
                    )
                    group_drop_option = dbc.DropdownMenuItem(
                        member,
                        id=group_drop_option_id,
                        n_clicks=1,
                        style={"fontSize": "larger", "fontFamily": FONT_FAMILY},
                    )
                    dropdown_menu_items.append(group_drop_option)
                    self.group_drop_options[group_drop_option_id] = group_drop_option

                group_drop_option_id = GROUP_DROP_OPTION_TEMPLATE.format(
                    collection, "all", ALL_GROUP_MEMBERS
                )
                group_drop_down_menu_item = dbc.DropdownMenuItem(
                    ALL_GROUP_MEMBERS,
                    id=group_drop_option_id,
                    n_clicks=1,
                    style={"fontSize": "larger", "fontFamily": FONT_FAMILY},
                )
                self.group_drop_options[group_drop_option_id] = (
                    group_drop_down_menu_item
                )
                dropdown_menu_items.append(group_drop_down_menu_item)

                group_dropdown_id = self.encode_group_dropdown(
                    collection, ALL_GROUP_MEMBERS
                )
                self.group_dropdown_menus[group_dropdown_id] = self._get_dropdown_menu(
                    group_dropdown_id, dropdown_menu_items, group_values[0]
                )

    def get(
        self, sub_component: str, sub_component_id_str, sub_config: Dict
    ) -> Component:
        self._setup_group_dropdown_menus()
        self._setup_variable_dropdown_menus()
        collection = self.feature_handler.get_default_collection()
        # For rendering scatterplots
        pointplot_fig = self.get_point_scatter_plot(collection)
        lineplot_fig = self.get_line_scatter_plot(collection)

        main_group_drop_down_menus = list(self.main_group_dropdown_menus.values())
        if len(main_group_drop_down_menus) > 0:
            main_group_drop_down_menus[0].style["display"] = "block"
        line_drop_down_menus = list(self.line_dropdown_menus.values())
        line_drop_down_menus[0].style["display"] = "block"

        upper_row = html.Div(
            [
                html.Div(
                    "Cruise",
                    className="col-auto px-1 m-2",
                    style={"color": FONT_COLOR, "fontFamily": FONT_FAMILY},
                ),
                html.Div(main_group_drop_down_menus, className="col-auto px-1"),
                html.Div(
                    "Variable",
                    className="col-auto px-1 m-2",
                    style={"color": FONT_COLOR, "fontFamily": FONT_FAMILY},
                ),
                html.Div(line_drop_down_menus, className="col-auto px-1"),
            ],
            className="row justify-content-center",
        )
        upper_components = [
            upper_row,
            dcc.Graph(
                id=SCATTER_PLOT_LINE_ID, figure=lineplot_fig, style={"height": "35.5vh"}
            ),
        ]
        group_drop_down_menus = list(self.group_dropdown_menus.values())
        group_drop_down_menus[0].style["display"] = "block"
        point_x_drop_down_menus = list(self.point_x_dropdown_menus.values())
        point_x_drop_down_menus[0].style["display"] = "block"
        point_y_drop_down_menus = list(self.point_y_dropdown_menus.values())
        point_y_drop_down_menus[0].style["display"] = "block"

        lower_row = html.Div(
            [
                html.Div(
                    "Station",
                    className="col-auto px-1 m-2",
                    style={"color": FONT_COLOR, "fontFamily": FONT_FAMILY},
                ),
                html.Div(group_drop_down_menus, className="col-auto px-1"),
                html.Div(
                    "X-Var",
                    className="col-auto px-1 m-2",
                    style={"color": FONT_COLOR, "fontFamily": FONT_FAMILY},
                ),
                html.Div(point_x_drop_down_menus, className="col-auto px-1"),
                html.Div(
                    "Y-Var",
                    className="col-auto px-1 m-2",
                    style={"color": FONT_COLOR, "fontFamily": FONT_FAMILY},
                ),
                html.Div(point_y_drop_down_menus, className="col-auto px-1"),
            ],
            className="row justify-content-center",
        )

        lower_components = [
            lower_row,
            dcc.Graph(
                id=SCATTER_PLOT_ID,
                figure=pointplot_fig,
                style={"height": "37vh"},
            ),
        ]
        sub_components = html.Div(
            [
                dbc.Col(
                    upper_components,
                    style={
                        "backgroundColor": PLOT_BGCOLOR,
                        "padding": "10px",
                        "width": "100%",
                    },
                ),
                dbc.Collapse(
                    id=COLLAPSE,
                    children=dbc.Col(
                        lower_components,
                        style={
                            "backgroundColor": PLOT_BGCOLOR,
                            "padding": "10px",
                            "width": "100%",
                        },
                    ),
                    is_open=len(lower_components) > 0,
                    className="mt-2",
                ),
            ],
        )

        return html.Div(
            children=[
                dcc.Store(id=COMPONENT_STORE_ID),
                dcc.Store(id=TEMP_STORE_ID),
                sub_components,
            ]
        )

    def get_point_scatter_plot(
        self,
        collection: str,
        selected_group_item: str = "",
        selected_main_group_item: str = "",
        x_variable: str = None,
        y_variable: str = None,
    ):
        df = self.get_dataframe(
            collection, selected_group_item, selected_main_group_item
        )
        levels = self.feature_handler.get_levels(collection)
        color_variable = levels[-1]
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
                color=color_variable,
                color_discrete_sequence=px.colors.qualitative.Set1,
                labels={
                    x_variable: self.title(x_variable),
                    y_variable: self.title(y_variable),
                    color_variable: self.title(color_variable),
                },
            )
            fig.update_layout(
                font=dict(family=FONT_FAMILY, size=18, color=FONT_COLOR),
                plot_bgcolor="rgb(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(marker_size=10)
            return fig

    @staticmethod
    def title(title: str) -> str:
        words = title.split(" ")
        for i, word in enumerate(words):
            if len(word) > 0 and word[0].isalpha():
                if len(word) > 1:
                    words[i] = word[0].upper() + word[1:]
                else:
                    words[i] = word[0].upper()
        return " ".join(words)

    def get_line_scatter_plot(
        self, collection: str, selected_main_group_item: str = "", variable: str = None
    ):
        df = self.get_dataframe(collection, ALL_GROUP_MEMBERS, selected_main_group_item)
        levels = self.feature_handler.get_levels(collection)
        order_variable = levels[-1]
        color_variable = levels[-2]
        df = df.sort_values(by=order_variable)
        if variable is None:
            variable = self.feature_handler.get_variables(collection)[0]
        fig = px.line(
            df,
            x=variable,
            y=order_variable,
            color=color_variable,
            line_shape="spline",
            render_mode="svg",
            markers=True,
            labels={
                variable: self.title(variable),
                order_variable: self.title(order_variable),
                color_variable: self.title(color_variable),
            },
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(title_text=self.title(variable))
        fig.update_yaxes(title_text=self.title(order_variable))
        fig.update_layout(font=dict(family=FONT_FAMILY, size=18, color=FONT_COLOR))
        fig.update_traces(marker=dict(size=10, color="yellow", symbol="circle"))
        fig.layout.plot_bgcolor = "rgb(0,0,0,0)"
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        fig.update_layout(legend_font_family=FONT_FAMILY)
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
        if main_group == ALL_GROUP_MEMBERS:
            group_values = list(nested_level_values.keys())
        else:
            group_values = list(nested_level_values.get(main_group).keys())
        group_values.sort()
        return group_values

    def get_dataframe(
        self,
        collection: str,
        selected_group_item: str = "",
        selected_main_group_item: str = "",
    ):
        df = self.feature_handler.get_df(collection)
        group_values, main_group_values = self._get_group_and_main_group_values(
            collection
        )
        levels = self.feature_handler.get_levels()
        if main_group_values is not None:
            main_group_item = (
                selected_main_group_item
                if selected_main_group_item != ""
                else main_group_values[0]
            )
            df = df[df[levels[-3]] == main_group_item]
        if selected_group_item != ALL_GROUP_MEMBERS:
            group_item = (
                selected_group_item if selected_group_item != "" else group_values[0]
            )
            df = df[df[levels[-2]] == group_item]
        return df

    @staticmethod
    def encode_main_group_dropdown(collection: str) -> str:
        return MAIN_GROUP_DROPDOWN_TEMPLATE.format(collection)

    @staticmethod
    def decode_main_group_dropdown(dropdown_id) -> str:
        return dropdown_id[MAIN_GROUP_DROPDOWN_OFFSET:]

    def encode_group_dropdown(self, collection: str, main_group: str) -> str:
        new_collection = collection.replace("_", "-")
        new_main_group = main_group.replace("_", "-")
        self._encodings[new_collection] = collection
        self._encodings[new_main_group] = main_group
        return GROUP_DROPDOWN_TEMPLATE.format(new_collection, new_main_group)

    def decode_group_dropdown(self, dropdown_id) -> Tuple[str, str]:
        ids = dropdown_id.split("_")
        collection = self._encodings.get(ids[-2], ids[-2])
        main_group = self._encodings.get(ids[-1], ids[-1])
        return collection, main_group

    @staticmethod
    def encode_xvar_dropdown(collection: str) -> str:
        return POINT_X_VAR_DROPDOWN_ID_TEMPLATE.format(collection)

    @staticmethod
    def decode_xvar_dropdown(dropdown_id: str) -> str:
        return dropdown_id[POINT_X_VAR_DROPDOWN_OFFSET:]

    @staticmethod
    def encode_yvar_dropdown(collection: str) -> str:
        return POINT_Y_VAR_DROPDOWN_ID_TEMPLATE.format(collection)

    @staticmethod
    def decode_yvar_dropdown(dropdown_id: str) -> str:
        return dropdown_id[POINT_Y_VAR_DROPDOWN_OFFSET:]

    @staticmethod
    def encode_linevar_dropdown(collection: str) -> str:
        return LINE_VAR_DROPDOWN_ID_TEMPLATE.format(collection)

    @staticmethod
    def decode_linevar_dropdown(dropdown_id: str) -> str:
        return dropdown_id[LINE_VAR_DROPDOWN_OFFSET:]

    def register_callbacks(self, component_ids: List[str], dashboard_id: str = None):

        group_dropdown_menus = list(self.group_dropdown_menus.keys())
        group_drop_options = list(self.group_drop_options.keys())

        line_dropdown_menus = list(self.line_dropdown_menus.keys())
        line_drop_options = list(self.xvar_drop_options.keys())

        point_x_dropdown_menus = list(self.point_x_dropdown_menus.keys())
        point_x_drop_options = list(self.point_x_drop_options.keys())

        point_y_dropdown_menus = list(self.point_y_dropdown_menus.keys())
        point_y_drop_options = list(self.point_y_drop_options.keys())

        main_group_dropdown_menus = list(self.main_group_dropdown_menus.keys())
        main_group_drop_options = list(self.main_group_drop_options.keys())

        if len(main_group_drop_options) > 0:

            @callback(
                Output(TEMP_STORE_ID, "data", allow_duplicate=True),
                [
                    Input(main_group_value_id, "n_clicks_timestamp")
                    for main_group_value_id in main_group_drop_options
                ],
                prevent_initial_call=True,
            )
            def selector_to_temp_main_group(*timestamps):
                if not any(timestamps):
                    return dash.no_update
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None)
                )
                selected_main_group_dropdown_id = list(
                    self.main_group_drop_options.keys()
                )[latest_timestamp_index]
                selected_main_group_item = self.main_group_drop_options[
                    selected_main_group_dropdown_id
                ].children
                temp = {MAIN_GROUP: selected_main_group_item}
                return temp

        @callback(
            Output(TEMP_STORE_ID, "data", allow_duplicate=True),
            [
                Input(group_value_id, "n_clicks_timestamp")
                for group_value_id in group_drop_options
            ],
            prevent_initial_call=True,
        )
        def selector_to_temp_group(*timestamps):
            if not any(timestamps):
                return dash.no_update
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None)
            )
            selected_group_dropdown_id = list(self.group_drop_options.keys())[
                latest_timestamp_index
            ]
            selected_group_item = self.group_drop_options[
                selected_group_dropdown_id
            ].children
            temp = {GROUP: selected_group_item}
            return temp

        @callback(
            Output(TEMP_STORE_ID, "data", allow_duplicate=True),
            [
                Input(point_x_drop_id, "n_clicks_timestamp")
                for point_x_drop_id in point_x_drop_options
            ],
            prevent_initial_call=True,
        )
        def selector_to_temp_xvar(*timestamps):
            if not any(timestamps):
                return dash.no_update
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None)
            )
            xvar_drop_option_id = list(self.xvar_drop_options.keys())[
                latest_timestamp_index
            ]
            xvar_drop_option_value = self.xvar_drop_options[
                xvar_drop_option_id
            ].children
            temp_data = {X_VARIABLE: xvar_drop_option_value}
            return temp_data

        @callback(
            Output(TEMP_STORE_ID, "data", allow_duplicate=True),
            [
                Input(point_y_drop_id, "n_clicks_timestamp")
                for point_y_drop_id in point_y_drop_options
            ],
            prevent_initial_call=True,
        )
        def selector_to_temp_yvar(*timestamps):
            if not any(timestamps):
                return dash.no_update
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None)
            )
            yvar_drop_option_id = list(self.point_y_drop_options.keys())[
                latest_timestamp_index
            ]
            yvar_drop_option_value = self.point_y_drop_options[
                yvar_drop_option_id
            ].children
            temp_data = {Y_VARIABLE: yvar_drop_option_value}
            return temp_data

        @callback(
            Output(TEMP_STORE_ID, "data", allow_duplicate=True),
            [
                Input(line_drop_id, "n_clicks_timestamp")
                for line_drop_id in line_drop_options
            ],
            prevent_initial_call=True,
        )
        def selector_to_temp_linevar(*timestamps):
            if not any(timestamps):
                return dash.no_update
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None)
            )
            line_drop_option_id = list(self.xvar_drop_options.keys())[
                latest_timestamp_index
            ]
            line_drop_option_value = self.xvar_drop_options[
                line_drop_option_id
            ].children
            temp_data = {LINE_VARIABLE: line_drop_option_value}
            return temp_data

        @callback(
            Output(f"{dashboard_id}-{GENERAL_STORE_ID}", "data", allow_duplicate=True),
            [Input(TEMP_STORE_ID, "data")],
            [State(f"{dashboard_id}-{GENERAL_STORE_ID}", "data")],
            prevent_initial_call=True,
        )
        def temp_to_general(temp_data, general_data):
            general_data = general_data or {}
            if COLLECTION not in general_data:
                general_data[COLLECTION] = self.feature_handler.get_default_collection()
            if GROUPS_SECTION not in general_data:
                general_data[GROUPS_SECTION] = {}
            collection = general_data[COLLECTION]
            if temp_data is not None:
                if collection not in general_data[GROUPS_SECTION]:
                    general_data[GROUPS_SECTION][collection] = {}
                if MAIN_GROUP in temp_data:
                    general_data[GROUPS_SECTION][collection][MAIN_GROUP] = temp_data[
                        MAIN_GROUP
                    ]
                    if GROUP in general_data[GROUPS_SECTION][collection]:
                        general_data[GROUPS_SECTION][collection].pop(GROUP)
                if GROUP in temp_data:
                    general_data[GROUPS_SECTION][collection][GROUP] = temp_data[GROUP]
            return general_data

        @callback(
            Output(COMPONENT_STORE_ID, "data"),
            [Input(TEMP_STORE_ID, "data")],
            [
                State(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
                State(COMPONENT_STORE_ID, "data"),
            ],
            prevent_initial_call=True,
        )
        def temp_to_component(temp_data, general_data, component_data):
            general_data = general_data or {}
            component_data = component_data or {}
            collection = general_data.get(
                COLLECTION, self.feature_handler.get_default_collection()
            )
            if VARIABLES_SECTION not in component_data:
                component_data[VARIABLES_SECTION] = {}
            selected_variable_fields = [X_VARIABLE, Y_VARIABLE, LINE_VARIABLE]
            if temp_data is not None:
                for field in selected_variable_fields:
                    if field in temp_data:
                        if collection not in component_data[VARIABLES_SECTION]:
                            component_data[VARIABLES_SECTION][collection] = {}
                        component_data[VARIABLES_SECTION][collection][field] = (
                            temp_data[field]
                        )
            return component_data

        if len(main_group_dropdown_menus) > 0:

            @callback(
                [
                    Output(main_group_dropdown_menu, "style")
                    for main_group_dropdown_menu in main_group_dropdown_menus
                ],
                [
                    Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
                ],
                prevent_initial_call=True,
            )
            def general_to_styles_main_group(data):
                if data is None or COLLECTION not in data:
                    return dash.no_update
                selected_collection = data.get(COLLECTION)
                selected_main_group_dropdown_id = self.encode_main_group_dropdown(
                    selected_collection
                )
                results = []
                for (
                    main_group_dropdown_menu_id,
                    main_group_dropdown_menu,
                ) in self.main_group_dropdown_menus.items():
                    if main_group_dropdown_menu_id == selected_main_group_dropdown_id:
                        results.append({"display": "block"})
                    else:
                        results.append({"display": "none"})
                return tuple(results)

        @callback(
            [
                Output(group_dropdown_menu, "style", allow_duplicate=True)
                for group_dropdown_menu in group_dropdown_menus
            ],
            [
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            ],
            prevent_initial_call=True,
        )
        def general_to_styles_group(general_data):
            if not general_data or COLLECTION not in general_data:
                return dash.no_update
            collection = general_data[COLLECTION]
            group_values, main_group_values = self._get_group_and_main_group_values(
                collection
            )
            main_group = (
                general_data.get(GROUPS_SECTION, {})
                .get(collection, {})
                .get(MAIN_GROUP, main_group_values[0])
            )
            selected_group_dropdown_id = self.encode_group_dropdown(
                collection, main_group
            )
            results = []
            for (
                group_dropdown_menu_id,
                group_dropdown_menu,
            ) in self.group_dropdown_menus.items():
                if group_dropdown_menu_id == selected_group_dropdown_id:
                    results.append({"display": "block"})
                else:
                    results.append({"display": "none"})
            return tuple(results)

        @callback(
            [
                Output(point_x_dropdown_menu, "style", allow_duplicate=True)
                for point_x_dropdown_menu in point_x_dropdown_menus
            ],
            [
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            ],
            prevent_initial_call=True,
        )
        def general_to_styles_xvar(selected_data):
            if selected_data is None or COLLECTION not in selected_data:
                return dash.no_update
            collection = selected_data[COLLECTION]
            selected_point_x_dropdown_id = self.encode_xvar_dropdown(collection)
            results = []
            for (
                point_x_dropdown_menu_id,
                point_x_dropdown_menu,
            ) in self.point_x_dropdown_menus.items():
                if point_x_dropdown_menu_id == selected_point_x_dropdown_id:
                    results.append({"display": "block"})
                else:
                    results.append({"display": "none"})
            return tuple(results)

        @callback(
            [
                Output(point_y_dropdown_menu, "style", allow_duplicate=True)
                for point_y_dropdown_menu in point_y_dropdown_menus
            ],
            [
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            ],
            prevent_initial_call=True,
        )
        def general_to_styles_yvar(selected_data):
            if selected_data is None or COLLECTION not in selected_data:
                return dash.no_update
            collection = selected_data[COLLECTION]
            selected_point_y_dropdown_id = self.encode_yvar_dropdown(collection)
            results = []
            for (
                point_y_dropdown_menu_id,
                point_y_dropdown_menu,
            ) in self.point_y_dropdown_menus.items():
                if point_y_dropdown_menu_id == selected_point_y_dropdown_id:
                    results.append({"display": "block"})
                else:
                    results.append({"display": "none"})
            return tuple(results)

        @callback(
            [
                Output(line_dropdown_menu, "style", allow_duplicate=True)
                for line_dropdown_menu in line_dropdown_menus
            ],
            [
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            ],
            prevent_initial_call=True,
        )
        def general_to_styles_linevar(selected_data):
            if selected_data is None or COLLECTION not in selected_data:
                return no_update
            collection = selected_data[COLLECTION]
            selected_line_dropdown_id = self.encode_linevar_dropdown(collection)
            results = []
            for (
                line_dropdown_menu_id,
                line_dropdown_menu,
            ) in self.line_dropdown_menus.items():
                if line_dropdown_menu_id == selected_line_dropdown_id:
                    results.append({"display": "block"})
                else:
                    results.append({"display": "none"})
            return tuple(results)

        if len(main_group_dropdown_menus) > 0:

            @callback(
                [
                    Output(main_group_dropdown_menu, "label")
                    for main_group_dropdown_menu in main_group_dropdown_menus
                ],
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
                prevent_initial_call=True,
            )
            def stores_to_labels_main_group(general_data):
                general_data = general_data or {}
                collection = general_data.get(
                    COLLECTION, self.feature_handler.get_default_collection()
                )
                main_group = (
                    general_data.get(GROUPS_SECTION, {})
                    .get(collection, {})
                    .get(MAIN_GROUP)
                )
                if main_group is None:
                    return dash.no_update
                relevant_main_group_dropdown_id = self.encode_main_group_dropdown(
                    collection
                )
                results = []
                for (
                    main_group_dropdown_menu_id,
                    main_group_dropdown_menu,
                ) in self.main_group_dropdown_menus.items():
                    if main_group_dropdown_menu_id == relevant_main_group_dropdown_id:
                        results.append(main_group)
                    else:
                        c = self.decode_main_group_dropdown(main_group_dropdown_menu_id)
                        _, main_groups = self._get_group_and_main_group_values(c)

                        results.append(main_groups[0])
                return tuple(results)

        @callback(
            [
                Output(group_dropdown_menu, "label")
                for group_dropdown_menu in group_dropdown_menus
            ],
            Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            prevent_initial_call=True,
        )
        def stores_to_labels_group(general_data):
            general_data = general_data or {}
            results = []
            for (
                group_dropdown_menu_id,
                group_dropdown_menu,
            ) in self.group_dropdown_menus.items():
                c, main_group = self.decode_group_dropdown(group_dropdown_menu_id)
                default_group = self._get_group_values_for_main_group(c, main_group)[0]
                group = (
                    general_data.get(GROUPS_SECTION, {})
                    .get(c, {})
                    .get(GROUP, default_group)
                )
                results.append(group)
            return tuple(results)

        @callback(
            [
                Output(x_dropdown_menu, "label")
                for x_dropdown_menu in point_x_dropdown_menus
            ],
            [
                Input(COMPONENT_STORE_ID, "data"),
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            ],
            prevent_initial_call=True,
        )
        def stores_to_labels_xvar(component_data, general_data):
            component_data = component_data or {}
            general_data = general_data or {}
            collection = general_data.get(
                COLLECTION, self.feature_handler.get_default_collection()
            )
            x_variable = (
                component_data.get(VARIABLES_SECTION, {})
                .get(collection, {})
                .get(X_VARIABLE)
            )
            if x_variable is None:
                return dash.no_update
            relevant_x_dropdown_menu_id = self.encode_xvar_dropdown(collection)
            results = []
            for (
                x_dropdown_menu_id,
                x_dropdown_menu,
            ) in self.point_x_dropdown_menus.items():
                if x_dropdown_menu_id == relevant_x_dropdown_menu_id:
                    results.append(x_variable)
                else:
                    c = self.decode_xvar_dropdown(x_dropdown_menu_id)
                    default_var = self.feature_handler.get_default_variable(c)
                    results.append(
                        component_data.get(VARIABLES_SECTION, {})
                        .get(c, {})
                        .get(X_VARIABLE, default_var)
                    )
            return tuple(results)

        @callback(
            [
                Output(y_dropdown_menu, "label")
                for y_dropdown_menu in point_y_dropdown_menus
            ],
            [
                Input(COMPONENT_STORE_ID, "data"),
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            ],
            prevent_initial_call=True,
        )
        def stores_to_labels_yvar(component_data, general_data):
            component_data = component_data or {}
            general_data = general_data or {}
            collection = general_data.get(
                COLLECTION, self.feature_handler.get_default_collection()
            )
            y_variable = (
                component_data.get(VARIABLES_SECTION, {})
                .get(collection, {})
                .get(Y_VARIABLE)
            )
            if y_variable is None:
                return dash.no_update
            relevant_y_dropdown_menu_id = self.encode_yvar_dropdown(collection)
            results = []
            for (
                y_dropdown_menu_id,
                y_dropdown_menu,
            ) in self.point_y_dropdown_menus.items():
                if y_dropdown_menu_id == relevant_y_dropdown_menu_id:
                    results.append(y_variable)
                else:
                    c = self.decode_yvar_dropdown(y_dropdown_menu_id)
                    default_var = self.feature_handler.get_variables()[-1]
                    results.append(
                        component_data.get(VARIABLES_SECTION, {})
                        .get(c, {})
                        .get(Y_VARIABLE, default_var)
                    )
            return tuple(results)

        @callback(
            [
                Output(line_dropdown_menu, "label")
                for line_dropdown_menu in line_dropdown_menus
            ],
            [
                Input(COMPONENT_STORE_ID, "data"),
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            ],
            prevent_initial_call=True,
        )
        def stores_to_labels_linevar(component_data, general_data):
            component_data = component_data or {}
            general_data = general_data or {}
            collection = general_data.get(
                COLLECTION, self.feature_handler.get_default_collection()
            )
            line_variable = (
                component_data.get(VARIABLES_SECTION, {})
                .get(collection, {})
                .get(LINE_VARIABLE)
            )
            if line_variable is None:
                return dash.no_update
            relevant_line_dropdown_menu_id = self.encode_linevar_dropdown(collection)
            results = []
            for (
                line_dropdown_menu_id,
                line_dropdown_menu,
            ) in self.line_dropdown_menus.items():
                if line_dropdown_menu_id == relevant_line_dropdown_menu_id:
                    results.append(line_variable)
                else:
                    c = self.decode_linevar_dropdown(line_dropdown_menu_id)
                    default_var = self.feature_handler.get_default_variable(c)
                    results.append(
                        component_data.get(VARIABLES_SECTION, {})
                        .get(c, {})
                        .get(LINE_VARIABLE, default_var)
                    )
            return tuple(results)

        @callback(
            [
                Output(SCATTER_PLOT_ID, "figure", allow_duplicate=True),
                Output(SCATTER_PLOT_LINE_ID, "figure", allow_duplicate=True),
            ],
            [
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
                Input(COMPONENT_STORE_ID, "data"),
            ],
            prevent_initial_call=True,
        )
        def stores_to_plots(general_data, component_data):
            component_data = component_data or {}
            if general_data is None or COLLECTION not in general_data:
                return no_update
            collection = general_data[COLLECTION]
            _, main_group_values = self._get_group_and_main_group_values(collection)
            if main_group_values is None:
                main_group = None
                default_group = self._get_group_values_for_main_group(
                    collection, ALL_GROUP_MEMBERS
                )[0]
            else:
                main_group = (
                    general_data.get(GROUPS_SECTION, {})
                    .get(collection, {})
                    .get(MAIN_GROUP, main_group_values[0])
                )
                default_group = self._get_group_values_for_main_group(
                    collection, main_group
                )[0]
            group = (
                general_data.get(GROUPS_SECTION, {})
                .get(collection, {})
                .get(GROUP, default_group)
            )
            variables = self.feature_handler.get_variables(collection)
            x_variable = (
                component_data.get(VARIABLES_SECTION, {})
                .get(collection, {})
                .get(X_VARIABLE, variables[0])
            )
            y_variable = (
                component_data.get(VARIABLES_SECTION, {})
                .get(collection, {})
                .get(Y_VARIABLE, variables[-1])
            )
            line_variable = (
                component_data.get(VARIABLES_SECTION, {})
                .get(collection, {})
                .get(LINE_VARIABLE, variables[0])
            )

            point_plot_fig = self.get_point_scatter_plot(
                collection, group, main_group, x_variable, y_variable
            )
            line_plot_fig = self.get_line_scatter_plot(
                collection, main_group, line_variable
            )
            return point_plot_fig, line_plot_fig

        @callback(
            Output(COLLAPSE, "is_open"),
            Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
        )
        def general_to_collapse(selected_data):
            if not selected_data or COLLECTION not in selected_data:
                return dash.no_update
            collection = selected_data[COLLECTION]
            variables = self.feature_handler.get_variables(collection)
            return len(variables) > 1
