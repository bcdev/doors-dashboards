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
                    "height": "80%"
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
        collection = self.feature_handler.get_collections()[0]
        df = self.feature_handler.get_df(collection)
        variables = self.feature_handler.get_variables(collection)
        time_column = self.feature_handler.get_time_column_name(collection)
        fig = make_subplots(
            cols=1, rows=len(variables), shared_xaxes='all',
            subplot_titles=variables
        )
        for i, selected_variable in enumerate(variables):
            fig.add_trace(
                go.Scatter(
                    x=df[time_column], y=df[selected_variable],
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
            showgrid=False
        )
        fig.update_yaxes(
            showticklabels=True,
            showgrid=False
        )
        fig.update_xaxes(
            row = 1,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(
                        count=1, label="1m", step="month", stepmode="backward"
                    ),
                    dict(
                        count=6, label="6m", step="month", stepmode="backward"
                    ),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward")
                ])
            )
        )

        return dcc.Graph(
            id=timeseries_id,
            figure=fig,
            style={
                'width': '100%',
                'height': '80vh'
            },
        )

    def _get_time_slider(self, time_slider_id: str) -> Component:
        collection = self.feature_handler.get_collections()[0]
        df = self.feature_handler.get_df(collection)
        time_column_name = self.feature_handler.get_time_column_name(collection)
        dt_time = pd.to_datetime(df[time_column_name])
        min_time = pd.Timestamp(min(dt_time))
        max_time = pd.Timestamp(max(dt_time))
        delta = (max_time - min_time) / 5
        marks = {}
        for j in range(6):
            v = min_time + j * delta
            marks[f'{v.to_datetime64()}'] = v.strftime("%Y-%m-%d")

        slider = dcc.RangeSlider(
            min_time.to_datetime64(),
            max_time.to_datetime64(),
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
            timestamp_range = [pd.Timestamp(v) for v in value]
            line_plots = self._get_timeplots(TIMEPLOTS_ID)
            line_plots.figure.update_xaxes(
                range=timestamp_range
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
            start = pd.Timestamp(relayout_data['xaxis.range[0]']).to_datetime64()
            end = pd.Timestamp(relayout_data['xaxis.range[1]']).to_datetime64()
            return [start, end]

        return app
