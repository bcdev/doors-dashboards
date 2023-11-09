from abc import ABC
from abc import abstractmethod
from dash.development.base_component import Component


class DashboardComponent(ABC):

    @abstractmethod
    def get(self, **kwargs) -> Component:
        pass
