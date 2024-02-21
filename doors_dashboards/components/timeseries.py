from dash import Dash
from dash import dcc
from dash import html
from dash import Input
from dash import Output
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict
from typing import List

from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler
from doors_dashboards.components.constant import FONT_COLOR
from doors_dashboards.components.constant import FONT_FAMILY
from doors_dashboards.components.constant import PLOT_BGCOLOR

TIMEGRAPH_ID = "timeplots_graph"
TIMEPLOTS_ID = "timeplots"
TIMESLIDER_ID = "timeslider"

VAR_DROPDOWN_ID_TEMPLATE = "ts_var_drop_down_id_{0}"  # collection
VAR_DROP_OPTION_TEMPLATE = \
    "ts_var_drop_option_id_{0}_{1}"  # collection variable
GROUP_DROPDOWN_ID_TEMPLATE = "ts_group_drop_down_id_{0}"  # collection
GROUP_DROP_OPTION_TEMPLATE = \
    "ts_group_drop_option_id_{0}_{1}"  # collection group


class TimeSeriesComponent(DashboardComponent):

    def __init__(self):
        self.features = None
        self.var_drop_menus = dict()
        self.var_drop_options = dict()
        self.group_drop_menus = dict()
        self.group_drop_options = dict()

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
                'display': 'none',
                'max-height': '300px !important', 'overflow-x': 'auto !important'

            },
            size="lg",
            color="secondary"
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
                    style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY}
                )
                self.var_drop_options[var_drop_option_id] = line_drop_option
                drop_menu_items.append(line_drop_option)
            var_dropdown_id = VAR_DROPDOWN_ID_TEMPLATE.format(collection)
            self.var_drop_menus[var_dropdown_id] = \
                self._get_dropdown_menu(
                    var_dropdown_id,
                    drop_menu_items,
                    variables[0]
                )

    def _get_group_and_main_group_values(self, collection: str):
        levels = self.feature_handler.get_levels()
        nested_level_values = self.feature_handler.get_nested_level_values(collection)
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
            group_values, main_group_values = \
                self._get_group_and_main_group_values(collection)
            group_drop_menu_items = []
            for member in group_values:
                group_drop_option_id = GROUP_DROP_OPTION_TEMPLATE.format(
                    collection, member
                )
                group_drop_option = \
                    dbc.DropdownMenuItem(
                        member,
                        id=group_drop_option_id,
                        n_clicks=1,
                        style={'fontSize': 'larger', 'fontfamily': FONT_FAMILY,
                               'max-height': '300px', 'overflow-x': 'auto'}
                    )
                group_drop_menu_items.append(group_drop_option)
                self.group_drop_options[group_drop_option_id] = \
                    group_drop_option
            group_dropdown_id = \
                GROUP_DROPDOWN_ID_TEMPLATE.format(collection)
            self.group_drop_menus[group_dropdown_id] = \
                self._get_dropdown_menu(
                    group_dropdown_id,
                    group_drop_menu_items,
                    group_values[0]
                )

    def get(self,
            sub_component: str, sub_component_id: str, sub_config: Dict
            ) -> Component:
        if sub_component == TIMEPLOTS_ID:
            self._setup_group_dropdown_menus()
            self._setup_variable_dropdown_menus()
            time_plots = self._get_timeplots(sub_component_id)

            var_drop_down_menus = list(self.var_drop_menus.values())
            var_drop_down_menus[0].style['display'] = 'block'

            group_drop_down_menus = list(self.group_drop_menus.values())
            group_drop_down_menus[0].style['display'] = 'block'

            row = dbc.Row([
                dbc.Col(
                    dbc.Label('Variable', style={'color': FONT_COLOR,
                                                 'fontFamily': FONT_FAMILY,
                                                 'fontSize': '25px',
                                                 'paddingTop': '5px'}),
                    className="col-sm-1"
                ),
                dbc.Col(
                    var_drop_down_menus,
                    className="col-sm-2"
                ),
                dbc.Col(
                    dbc.Label('Duration', style={'color': FONT_COLOR,
                                                 'fontFamily': FONT_FAMILY,
                                                 'fontSize': '25px',
                                                 'paddingTop': '5px'}),
                    className="col-sm-1"
                ),
                dbc.Col(
                    group_drop_down_menus,
                    className="col-sm-2"
                )
            ])
            sub_components = [
                dbc.Col(
                    html.Div(
                        children=[
                            row,
                            time_plots
                        ],
                        style={'backgroundColor': PLOT_BGCOLOR,
                               'padding': '10px',
                               'border-radius': '15px'}
                    ),
                    className='col-lg-12',
                    style={
                        'marginBottom': '15px'
                    }
                )
            ]
            return dbc.Row(sub_components)
        if sub_component == TIMESLIDER_ID:
            time_slider = self._get_time_slider(sub_component_id)
            return html.Div(
                id=f"{sub_component_id}_div",
                children=[
                    time_slider
                ], style={
                    "margin": "10px",
                    "paddingLeft": "6.5%",
                    "paddingRight": "6.5%",
                    "height": "10%"
                }
            )
        raise ValueError(f"Unknown subcomponent {sub_component} passed to "
                         f"'timeplots'. Must be one of 'timeplots', "
                         f"'timeslider'.")

    def _get_timeplots(self, timeseries_id: str) -> Component:
        df = self.feature_handler.get_df()
        variables = self.feature_handler.get_variables()
        time_column = self.feature_handler.get_time_column_name()
        fig = make_subplots(
            cols=1, rows=len(variables), shared_xaxes='all',
            subplot_titles=variables
        )
        for i, selected_variable in enumerate(variables):
            fig.add_trace(
                go.Scatter(
                    x=pd.to_datetime(df[time_column]),
                    y=df[selected_variable],
                    name=selected_variable,
                    textfont={
                        'family': 'Roboto, Helvetica, Arial, sans-serif',
                        'size': 20
                    }),
                col=1, row=i + 1)
            break
        fig.update_layout(
            font=dict(family=FONT_FAMILY, size=20, color=FONT_COLOR),
            plot_bgcolor="rgb(0,0,0,0)",
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )

        fig.update_layout(
            xaxis_tickformatstops=[
                dict(dtickrange=[None, 1000], value="%H:%M:%S.%L\n%e. %b %y"),
                dict(dtickrange=[1000, 60000], value="%H:%M:%S\n%e. %b %y"),
                dict(dtickrange=[60000, 86400000], value="%H:%M\n%e. %b %y"),
                dict(dtickrange=[86400000, 604800000], value="%e. %b %y"),
                dict(dtickrange=[604800000, "M12"], value="%b %y"),
                dict(dtickrange=["M12", None], value="%Y")
            ]
        )

        fig.update_xaxes(
            showticklabels=True,
            showgrid=False,
            nticks=10,
            type="date"
        )
        fig.update_yaxes(
            showticklabels=True,
            showgrid=False
        )
        min_time, max_time = self.feature_handler.get_time_range()
        delta = max_time - min_time
        range_list = [
            dict(count=1, label="1h", step="hour", stepmode="backward"),
            dict(count=1, label="1d", step="day", stepmode="backward")
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
            rangeslider=dict(
                visible=True,
            ),
            rangeselector=dict(
                buttons=list(range_list),
                bgcolor="black",
            )
        )

        return dcc.Graph(
            id=timeseries_id,
            figure=fig,
        )

    def _get_time_slider(self, time_slider_id: str) -> Component:
        min_time, max_time = self.feature_handler.get_time_range()
        delta = (max_time - min_time) / 5
        marks = {}
        for j in range(6):
            v = min_time + j * delta
            marks[int((v - min_time).total_seconds())] = \
                v.strftime("%Y-%m-%d %H:%M:%S")

        slider = dcc.RangeSlider(
            0,
            int((max_time - min_time).total_seconds()),
            marks=marks,
            id=time_slider_id
        )
        return slider

    def set_feature_handler(self, feature_handler: FeatureHandler):
        self.feature_handler = feature_handler

    def register_callbacks(self, app: Dash, component_ids: Dict[str, str]):
        @app.callback(
            Output(TIMEGRAPH_ID, 'children'),
            Input(TIMESLIDER_ID, 'value')
        )
        def update_timeplots(value):
            if value is None:
                raise PreventUpdate
            min_time, _ = self.feature_handler.get_time_range()
            timestamp_range = [min_time + pd.Timedelta(seconds=v)
                               for v in value]
            line_plots = self._get_timeplots(TIMEPLOTS_ID)
            line_plots.figure.update_xaxes(
                range=timestamp_range,
            )
            return line_plots

        @app.callback(
            Output(TIMESLIDER_ID, 'value'),
            Input(TIMEPLOTS_ID, 'relayoutData')
        )
        def update_timeslider(relayout_data):
            if relayout_data is None or \
                    'xaxis.range[0]' not in relayout_data or \
                    'xaxis.range[1]' not in relayout_data:
                raise PreventUpdate
            min_time, _ = self.feature_handler.get_time_range()
            start = int((pd.Timestamp(
                relayout_data['xaxis.range[0]']) - min_time
                         ).total_seconds())
            end = int((pd.Timestamp(
                relayout_data['xaxis.range[1]']) - min_time
                       ).total_seconds())
            return [start, end]

        return app
