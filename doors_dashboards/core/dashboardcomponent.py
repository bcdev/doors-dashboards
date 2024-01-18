from abc import ABC
from abc import abstractmethod
from typing import Dict

from dash import Dash
from dash.development.base_component import Component


class DashboardComponent(ABC):

    @abstractmethod
    def get(self, **kwargs) -> Component:
        pass

    @abstractmethod
    def register_callbacks(self, app: Dash, component_ids: Dict[str, str]):
        pass
