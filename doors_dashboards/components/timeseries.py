from dash import dcc
from dash import html
from dash import Input
from dash import no_update
from dash import Output
from dash import State
from dash import callback
from dash.development.base_component import Component
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict
from typing import List
from typing import Optional

from doors_dashboards.components.constant import (
    COLLECTION,
    FONT_FAMILY,
    SCATTER_FONT_SIZE,
    FONT_COLOR,
    GROUPS_SECTION,
    PLOT_BGCOLOR,
    GENERAL_STORE_ID,
)

from doors_dashboards.core.constants import LOG
from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

TIMEGRAPH_ID = "timeplots_graph"
TIMEPLOTS_ID = "timeplots"
TIMESLIDER_ID = "timeslider"

VAR_DROPDOWN_ID_TEMPLATE = "ts_var_drop_down_id_{0}"  # collection
VAR_DROP_OPTION_TEMPLATE = "ts_var_drop_option_id_{0}_{1}"  # collection variable
GROUP_DROPDOWN_ID_TEMPLATE = "ts_group_drop_down_id_{0}"  # collection
GROUP_DROP_OPTION_TEMPLATE = "ts_group_drop_option_id_{0}_{1}"  # collection group


class TimeSeriesComponent(DashboardComponent):

    def __init__(self, dashboard_id: str = None):
        self.features = None
        self.var_drop_menus = dict()
        self.var_drop_options = dict()
        self.group_drop_menus = dict()
        self.group_drop_options = dict()
        self._dashboard_id = dashboard_id

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
            drop_menu_items = []
            for variable in variables:
                var_drop_option_id = VAR_DROP_OPTION_TEMPLATE.format(
                    collection, variable
                )
                line_drop_option = dbc.DropdownMenuItem(
                    variable,
                    id=var_drop_option_id,
                    n_clicks=1,
                    style={"fontSize": SCATTER_FONT_SIZE, "fontFamily": FONT_FAMILY},
                )
                self.var_drop_options[var_drop_option_id] = line_drop_option
                drop_menu_items.append(line_drop_option)
            var_dropdown_id = VAR_DROPDOWN_ID_TEMPLATE.format(collection)
            self.var_drop_menus[var_dropdown_id] = self._get_dropdown_menu(
                var_dropdown_id, drop_menu_items, variables[0]
            )

    def _get_group_and_main_group_values(self, collection: str):
        levels = self.feature_handler.get_levels()
        nested_level_values = self.feature_handler.get_nested_level_values(collection)
        if len(levels) == 0:
            return None, None
        if len(levels) == 1:
            group_values = nested_level_values
            group_values.sort()
            return group_values, None
        if len(levels) == 2:
            group_values = list(nested_level_values.keys())
            group_values.sort()
            return group_values, None
        else:
            main_group_values = list(nested_level_values.keys())
            main_group_values.sort()
            group_values = list(nested_level_values.get(main_group_values[0]).keys())
            group_values.sort()
            return group_values, main_group_values

    def _setup_group_dropdown_menus(self):
        collections = self.feature_handler.get_collections()
        for collection in collections:
            group_values, main_group_values = self._get_group_and_main_group_values(
                collection
            )
            group_drop_menu_items = []
            if group_values is None:
                return
            for member in group_values:
                group_drop_option_id = GROUP_DROP_OPTION_TEMPLATE.format(
                    collection, member
                )
                group_drop_option = dbc.DropdownMenuItem(
                    member,
                    id=group_drop_option_id,
                    n_clicks=1,
                    style={"fontSize": SCATTER_FONT_SIZE, "fontFamily": FONT_FAMILY},
                )
                group_drop_menu_items.append(group_drop_option)
                self.group_drop_options[group_drop_option_id] = group_drop_option
            group_dropdown_id = GROUP_DROPDOWN_ID_TEMPLATE.format(collection)
            self.group_drop_menus[group_dropdown_id] = self._get_dropdown_menu(
                group_dropdown_id, group_drop_menu_items, group_values[0]
            )

    def get(
        self, sub_component: str, sub_component_id: str, sub_config: Dict
    ) -> Component:
        if sub_component == TIMEPLOTS_ID:
            self._setup_group_dropdown_menus()
            self._setup_variable_dropdown_menus()
            time_plots = self._get_timeplots(sub_component_id)
            time_div = html.Div(
                id=f"{self._dashboard_id}-{TIMEGRAPH_ID}", children=[time_plots]
            )

            var_drop_down_menus = list(self.var_drop_menus.values())
            var_drop_down_menus[0].style["display"] = "block"

            row_children = [
                html.Div(
                    "Variable:",
                    className="col-auto px-1 m-2",
                    style={"color": FONT_COLOR, "fontFamily": FONT_FAMILY},
                ),
                html.Div(var_drop_down_menus, className="col-auto px-1"),
            ]

            group_drop_down_menus = list(self.group_drop_menus.values())

            if len(group_drop_down_menus) > 0:
                group_drop_down_menus[0].style["display"] = "block"
                title = self.feature_handler.get_levels()[-1].title()
                row_children.append(
                    html.Div(
                        f"{title}:",
                        className="col-auto px-1 m-2",
                        style={"color": FONT_COLOR, "fontFamily": FONT_FAMILY},
                    )
                )
                row_children.append(
                    html.Div(group_drop_down_menus, className="col-auto px-1")
                )
            row = html.Div(row_children, className="row justify-content-center")

            sub_components = [
                dbc.Col(
                    html.Div(
                        children=[row, time_div],
                        style={
                            "backgroundColor": PLOT_BGCOLOR,
                            "padding": "10px",
                        },
                    ),
                    className="col-lg-12",
                    style={"marginBottom": "15px"},
                )
            ]
            return dbc.Row(sub_components)
        if sub_component == TIMESLIDER_ID:
            time_slider = self._get_time_slider(sub_component_id)
            return html.Div(
                id=f"{sub_component_id}_div",
                children=[time_slider],
                style={
                    "margin": "10px",
                    "paddingLeft": "6.5%",
                    "paddingRight": "6.5%",
                    "height": "10%",
                },
            )
        raise ValueError(
            f"Unknown subcomponent {sub_component} passed to "
            f"'timeplots'. Must be one of 'timeplots', "
            f"'timeslider'."
        )

    def _get_timeplots(
        self,
        timeseries_id: str,
        *,
        collection: Optional[str] = None,
        variable: Optional[str] = None,
        group: Optional[str] = None,
    ) -> Component:
        collection = collection or self.feature_handler.get_default_collection()
        variable = variable or self.feature_handler.get_default_variable(collection)
        df = self.feature_handler.get_df(collection)

        if group is None:
            group_values, _ = self._get_group_and_main_group_values(collection)
            if group_values is not None and len(group_values) > 0:
                group = group_values[0]
        if group is not None:
            level = self.feature_handler.get_levels(collection)[0]
            df = df[df[level] == group]
        time_column = self.feature_handler.get_time_column_name(collection)
        df[time_column] = pd.to_datetime(df[time_column])
        df = df.sort_values(by=time_column)
        fig = make_subplots(
            cols=1,
            rows=1,
        )
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(df[time_column]),
                y=df[variable],
                name=variable,
                textfont={
                    "family": FONT_FAMILY,
                },
            ),
            col=1,
            row=1,
        )
        fig.update_layout(
            font=dict(family=FONT_FAMILY, size=18, color=FONT_COLOR),
            plot_bgcolor="rgb(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )

        fig.update_layout(
            xaxis_tickformatstops=[
                dict(dtickrange=[None, 1000], value="%H:%M:%S.%L\n%e. %b %y"),
                dict(dtickrange=[1000, 60000], value="%H:%M:%S\n%e. %b %y"),
                dict(dtickrange=[60000, 86400000], value="%H:%M\n%e. %b %y"),
                dict(dtickrange=[86400000, 604800000], value="%e. %b %y"),
                dict(dtickrange=[604800000, "M12"], value="%b %y"),
                dict(dtickrange=["M12", None], value="%Y"),
            ]
        )

        fig.update_xaxes(showticklabels=True, showgrid=False, nticks=10, type="date")
        fig.update_yaxes(title=variable.title(), showticklabels=True, showgrid=False)
        min_time = min(df[time_column])
        max_time = max(df[time_column])
        delta = max_time - min_time
        range_list = [
            dict(count=1, label="1h", step="hour", stepmode="backward"),
            dict(count=1, label="1d", step="day", stepmode="backward"),
        ]
        if delta > pd.Timedelta(days=1):
            range_list.append(
                dict(count=7, label="1w", step="day", stepmode="backward")
            )
        if delta > pd.Timedelta(days=7):
            range_list.append(
                dict(count=1, label="1m", step="month", stepmode="backward")
            )
        if delta > pd.Timedelta(days=28):
            range_list.append(
                dict(count=6, label="6m", step="month", stepmode="backward")
            )
            range_list.append(
                dict(count=1, label="YTD", step="year", stepmode="todate")
            )
            range_list.append(
                dict(count=1, label="1y", step="year", stepmode="backward")
            )

        fig.update_xaxes(
            row=1,
            rangeslider_visible=True,
            rangeselector=dict(buttons=list(range_list)),
        )
        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeselector_font_color="white",
            xaxis_rangeselector_activecolor="#5c636a",
            xaxis_rangeselector_bgcolor="#6c757d",
        )

        return dcc.Graph(
            id=timeseries_id, figure=fig, style={"width": "100%", "height": "60vh"}
        )

    def _get_time_slider(self, time_slider_id: str) -> Component:
        min_time, max_time = self.feature_handler.get_time_range()
        delta = (max_time - min_time) / 5
        marks = {}
        for j in range(6):
            v = min_time + j * delta
            marks[int((v - min_time).total_seconds())] = v.strftime("%Y-%m-%d %H:%M:%S")

        slider = dcc.RangeSlider(
            0,
            int((max_time - min_time).total_seconds()),
            marks=marks,
            id=time_slider_id,
        )
        return slider

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def register_callbacks(self, component_ids: Dict[str, str], dashboard_id: str):
        group_drop_menus = list(self.group_drop_menus.keys())
        group_drop_options = list(self.group_drop_options.keys())

        var_drop_menus = list(self.var_drop_menus.keys())
        var_drop_options = list(self.var_drop_options.keys())

        @callback(
            Output(f"{dashboard_id}-{GENERAL_STORE_ID}", "data", allow_duplicate=True),
            Input(f"{dashboard_id}-variable_selector", "data"),
            State(f"{dashboard_id}-general", "data"),
            prevent_initial_call=True,
        )
        def update_general_store_after_variable_selection(selected_data, general_data):
            if selected_data is None:
                return no_update
            general_data = general_data or {}
            if COLLECTION not in general_data:
                general_data[COLLECTION] = self.feature_handler.get_default_collection()
            if "variables" not in general_data:
                general_data["variables"] = {}
            collection = general_data[COLLECTION]
            general_data["variables"][collection] = selected_data["selected_var"]
            return general_data

        @callback(
            Output(f"{dashboard_id}-variable_selector", "data"),
            [
                Input(var_drop_id, "n_clicks_timestamp")
                for var_drop_id in var_drop_options
            ],
        )
        def update_variable_selector_store(*timestamps):
            if not any(timestamps):
                return no_update
            latest_timestamp_index = timestamps.index(
                max(t for t in timestamps if t is not None)
            )

            var_drop_option_id = list(self.var_drop_options.keys())[
                latest_timestamp_index
            ]
            selected_var = self.var_drop_options[var_drop_option_id].children
            return {"selected_var": selected_var}

        @callback(
            [Output(var_drop_menu, "label") for var_drop_menu in var_drop_menus],
            Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
        )
        def update_variable_drop_down_labels(general_data):
            if general_data is None:
                return no_update
            general_data = general_data or {}
            id_to_var = {}
            for collection, variable in general_data.get("variables", {}).items():
                var_drop_menu = VAR_DROPDOWN_ID_TEMPLATE.format(collection)
                id_to_var[var_drop_menu] = variable
            results = []
            for var_drop_menu_id, var_drop_menu in self.var_drop_menus.items():
                results.append(id_to_var.get(var_drop_menu_id, ""))
            return tuple(results)

        if len(group_drop_options) > 0:

            @callback(
                Output(
                    f"{dashboard_id}-{GENERAL_STORE_ID}", "data", allow_duplicate=True
                ),
                Input(f"{dashboard_id}-group_selector", "data"),
                State(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
                prevent_initial_call=True,
            )
            def update_general_store_after_group_selection(selected_data, general_data):
                if selected_data is None:
                    return no_update
                general_data = general_data or {}
                if COLLECTION not in general_data:
                    general_data[COLLECTION] = (
                        self.feature_handler.get_default_collection()
                    )
                if GROUPS_SECTION not in general_data:
                    general_data[GROUPS_SECTION] = {}
                collection = general_data[COLLECTION]
                general_data[GROUPS_SECTION][collection] = selected_data[GROUPS_SECTION]
                return general_data

            @callback(
                Output(f"{dashboard_id}-group_selector", "data"),
                [
                    Input(group_drop_id, "n_clicks_timestamp")
                    for group_drop_id in group_drop_options
                ],
            )
            def update_group_selector_store(*timestamps):
                if not any(timestamps):
                    return no_update
                latest_timestamp_index = timestamps.index(
                    max(t for t in timestamps if t is not None)
                )

                group_drop_option_id = list(self.group_drop_options.keys())[
                    latest_timestamp_index
                ]
                selected_group = self.group_drop_options[group_drop_option_id].children
                return {GROUPS_SECTION: selected_group}

            @callback(
                [
                    Output(group_drop_menu, "label")
                    for group_drop_menu in group_drop_menus
                ],
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            )
            def update_group_drop_down_labels(general_data):
                if general_data is None:
                    return no_update
                general_data = general_data or {}
                id_to_group = {}
                for collection, group in general_data.get(GROUPS_SECTION, {}).items():
                    group_drop_menu = GROUP_DROPDOWN_ID_TEMPLATE.format(collection)
                    id_to_group[group_drop_menu] = group
                results = []
                for (
                    group_drop_menu_id,
                    group_drop_menu,
                ) in self.group_drop_menus.items():
                    results.append(id_to_group.get(group_drop_menu_id, ""))
                return tuple(results)

        @callback(
            Output(f"{self._dashboard_id}-{TIMEGRAPH_ID}", "children"),
            Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
        )
        def update_time_plots_after_general_data_change(general_data):
            if general_data is None:
                return no_update
            LOG.debug(f"Updating time plot for dashboard '{dashboard_id}'")
            collection = general_data[COLLECTION]
            variable = general_data.get("variables", {}).get(collection)
            LOG.debug(f"Mapping of collection to group: "
                      f"'{general_data.get(GROUPS_SECTION, {})}'")
            LOG.debug(
                f"Collection group: "
                f"'{general_data.get(GROUPS_SECTION, {}).get(collection, {})}'"
            )
            group = (
                general_data.get(GROUPS_SECTION, {}).get(collection)
            )
            line_plots = self._get_timeplots(
                TIMEPLOTS_ID, collection=collection, variable=variable, group=group
            )
            return line_plots

        variable_style_outputs = [
            Output(variable_drop_menu, "style") for variable_drop_menu in var_drop_menus
        ]

        variable_label_outputs = [
            Output(variable_drop_menu, "label", allow_duplicate=True)
            for variable_drop_menu in var_drop_menus
        ]
        variable_outputs = variable_style_outputs + variable_label_outputs

        @callback(
            variable_outputs,
            Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
            prevent_initial_call=True,
        )
        def update_variable_outputs(general_data):
            if general_data is None or COLLECTION not in general_data:
                return no_update
            collection = general_data.get(COLLECTION)
            selected_variable_dropdown_id = VAR_DROPDOWN_ID_TEMPLATE.format(collection)
            results = []
            for var_drop_menu_id, var_drop_menu in self.var_drop_menus.items():
                if var_drop_menu_id == selected_variable_dropdown_id:
                    results.append({"display": "block"})
                else:
                    results.append({"display": "none"})
            for var_drop_menu_id, var_drop_menu in self.var_drop_menus.items():
                if var_drop_menu_id == selected_variable_dropdown_id:
                    variable = general_data.get("variables", {}).get(
                        collection,
                        self.feature_handler.get_default_variable(collection),
                    )
                    results.append(variable)
                else:
                    results.append("")
            return tuple(results)

        group_style_outputs = [
            Output(group_drop_menu, "style") for group_drop_menu in group_drop_menus
        ]

        group_label_outputs = [
            Output(group_drop_menu, "label", allow_duplicate=True)
            for group_drop_menu in group_drop_menus
        ]
        group_outputs = group_style_outputs + group_label_outputs

        if len(group_outputs) > 0:

            @callback(
                group_outputs,
                Input(f"{dashboard_id}-{GENERAL_STORE_ID}", "data"),
                prevent_initial_call=True,
            )
            def update_group_outputs(general_data):
                if general_data is None or COLLECTION not in general_data:
                    return no_update
                collection = general_data.get(COLLECTION)
                selected_group_dropdown_id = GROUP_DROPDOWN_ID_TEMPLATE.format(
                    collection
                )
                results = []
                for (
                    group_drop_menu_id,
                    group_drop_menu,
                ) in self.group_drop_menus.items():
                    if group_drop_menu_id == selected_group_dropdown_id:
                        results.append({"display": "block"})
                    else:
                        results.append({"display": "none"})
                for (
                    group_drop_menu_id,
                    group_drop_menu,
                ) in self.group_drop_menus.items():
                    if group_drop_menu_id == selected_group_dropdown_id:
                        group_values, _ = self._get_group_and_main_group_values(
                            collection
                        )
                        group = general_data.get(GROUPS_SECTION, {}).get(
                            collection, group_values[0]
                        )
                        num_items = len(group_values)
                        if num_items > 10:
                            max_height = "200px"
                            overflow_y = "scroll"
                            group_drop_menu.style.update(
                                {
                                    "maxHeight": max_height,
                                    "overflowY": overflow_y,
                                    "overflowX": "hidden",  # Hide horizontal scrollbar
                                }
                            )
                        results.append(group)
                    else:
                        results.append("")
                return tuple(results)
