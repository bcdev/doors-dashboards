import pandas as pd
import plotly.express as px
from dash import dcc
from dash.development.base_component import Component

from doors_dashboards.core.dashboardcomponent import DashboardComponent


class TimeSeriesComponent(DashboardComponent):

    def get(self, df: pd.DataFrame, selected_variable: str, timeseries_id: str, **kwargs) -> Component:
        fig = px.line(df, x=df.timestamp, y=selected_variable,
                      hover_data={"timestamp": "|%B %d, %Y %H:%M"},
                      )
        fig.update_layout(
            plot_bgcolor='aliceblue'
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
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
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
