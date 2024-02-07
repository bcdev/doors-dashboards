from dash import Dash
from dash import dcc
from dash import html
from dash import Input
from dash import Output
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict

from doors_dashboards.core.dashboardcomponent import DashboardComponent
from doors_dashboards.core.featurehandler import FeatureHandler

TIMEGRAPH_ID = "timeplots_graph"
TIMEPLOTS_ID = "timeplots"
TIMESLIDER_ID = "timeslider"


class TimeSeriesComponent(DashboardComponent):

    def __init__(self):
        self.features = None

    def get(self,
            sub_component: str, sub_component_id: str, sub_config: Dict
    ) -> Component:
        if sub_component == TIMEPLOTS_ID:
            time_plots = self._get_timeplots(sub_component_id)
            return html.Div(
                id=TIMEGRAPH_ID,
                children=[
                    time_plots
                ], style={
                    "margin": "10px",
                    "height": "90%"
                }
            )
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
                    }),
                col=1, row=i + 1)
        fig.update_layout(
            plot_bgcolor='aliceblue',
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
            rangeselector=dict(
                buttons=list(range_list)
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
