from dash import dcc
from dash.development.base_component import Component
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List

from doors_dashboards.core.dashboardcomponent import DashboardComponent


class TimeSeriesComponent(DashboardComponent):

    def get(self, df: pd.DataFrame, selected_variables: List[str],
            timeseries_id: str, **kwargs) -> Component:
        fig = make_subplots(
            cols=1, rows=len(selected_variables), shared_xaxes='all',
        )
        for i, selected_variable in enumerate(selected_variables):
            fig.add_trace(
                go.Scatter(x=df.timestamp, y=df[selected_variable]),
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
                'height': '100%'
            },
        )
