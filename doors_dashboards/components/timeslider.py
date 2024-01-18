from dash import Dash
from dash import dcc
from dash.development.base_component import Component
import pandas as pd
from typing import Dict

from doors_dashboards.core.dashboardcomponent import DashboardComponent


class TimeSliderComponent(DashboardComponent):

    def get(self, df: pd.DataFrame, id: str, **kwargs) -> Component:
        min_time = pd.Timestamp(min(df.timestamp))
        max_time = pd.Timestamp(max(df.timestamp))
        delta = (max_time - min_time) / 5
        marks = {}
        for j in range(6):
            v = min_time + j * delta
            marks[f'{v.toordinal()}'] = v.strftime("%Y-%m-%d")

        slider = dcc.RangeSlider(
            min_time.toordinal(),
            max_time.toordinal(),
            marks=marks,
            id=id
        )
        return slider

    def register_callbacks(self, app: Dash, component_ids: Dict[str, str]):
        pass
