from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List

from dash import Dash
from dash.development.base_component import Component

from doors_dashboards.core.featurehandler import FeatureHandler


class DashboardComponent(ABC):

    @abstractmethod
    def get(self,
            sub_component: str, sub_component_id_str, sub_config: Dict
            ) -> Component:
        pass

    @abstractmethod
    def set_feature_handler(self, feature_handler: FeatureHandler):
        pass

    @abstractmethod
    def register_callbacks(self, component_ids: List[str],
                           dashboard_id: str):
        pass
