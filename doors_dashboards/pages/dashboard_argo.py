import yaml
import os
import dash
from typing import Dict

from doors_dashboards.dashboards.dashboard import create_dashboard

dash.register_page(__name__,title='Black Sea Argo Floats ',
    name='Black Sea Argo Floats')

_CONFIGS_PATH = "../../configs"


def _read_config(id: str) -> Dict:
    return _read_config_file(f"{id}.yml")


def _read_config_file(config_filename: str) -> Dict:
    #print(os.getcwd())
    config_path = os.path.join(_CONFIGS_PATH, config_filename)
    with open(config_path, "r", encoding="utf-8") as config_stream:
        return yaml.safe_load(config_stream)


def serve_layout(dashboard_id: str):
    dashboard_config = _read_config(dashboard_id)
    dashboard_layout = create_dashboard(dashboard_config)
    return dashboard_layout


layout = serve_layout("argo")
