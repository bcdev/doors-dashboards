import yaml
import os
import dash
from typing import Dict

from doors_dashboards.components.constant import CONFIGS_PATH
from doors_dashboards.dashboards.dashboard import create_dashboard

dash.register_page(__name__, title='Bulgaria MAF Meteograms',
                   name='Bulgaria MAF Meteograms')


def _read_config(id: str) -> Dict:
    return _read_config_file(f"{id}.yml")


def _read_config_file(config_filename: str) -> Dict:
    print(os.getcwd())
    file_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(file_dir, CONFIGS_PATH, config_filename)
    with open(config_path, "r", encoding="utf-8") as config_stream:
        return yaml.safe_load(config_stream)


def serve_layout(dashboard_id: str):
    dashboard_config = _read_config(dashboard_id)
    dashboard_layout = create_dashboard(dashboard_config)
    return dashboard_layout


layout = serve_layout("bg1")