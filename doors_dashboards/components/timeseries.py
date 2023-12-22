import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.development.base_component import Component

from doors_dashboards.core.dashboardcomponent import DashboardComponent


class TimeSeriesComponent(DashboardComponent):

    def get(self, df: pd.DataFrame, selected_variable: str, timeseries_id: str, **kwargs) -> Component:
        fig = px.line(df, x=df.timestamp, y=selected_variable,
                      hover_data={"timestamp": "|%B %d, %Y"},
                      )
        fig.update_layout(
            plot_bgcolor='aliceblue'
        )
        fig.update_xaxes(
            dtick="D1",
            tickformat="%b\n%Y",
            ticklabelmode="period")

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        return dcc.Graph(
            id=timeseries_id,
            figure=fig,
            style={'height': '300px', 'width': '100%'},
        )
