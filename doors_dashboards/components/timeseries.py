import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.development.base_component import Component

from doors_dashboards.core.dashboardcomponent import DashboardComponent


class TimeSeriesComponent(DashboardComponent):

    def get(self, df: pd.DataFrame, selected_variable: list[str], timeseries_id: str, **kwargs) -> Component:
        fig = px.line(df, x=df.timestamp, y=selected_variable,
                      hover_data={"timestamp": "|%B %d, %Y"},
                      )
        fig.update_xaxes(
            dtick="M1",
            tickformat="%b\n%Y",
            ticklabelmode="period")

        return dcc.Graph(
            id=timeseries_id,
            figure=fig,
            style={'height': '1000px','width': '100%' },
        )
