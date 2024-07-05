from dash import register_page
import os
from pathlib import Path
from typing import Dict
from typing import List
import yaml

from doors_dashboards.core.constants import LOG
from doors_dashboards.dashboards.dashboard import create_dashboard

CONFIGS_PATH = "../configs"


def _get_blocked_ids() -> List[str]:
    blocked_ids = []
    with open(os.path.join(CONFIGS_PATH, "blocklist.txt"), "r") as bl:
        for line in bl:
            blocked_ids.append(line.strip())
    return blocked_ids


def _get_dashboard_ids() -> List[str]:
    p = Path(CONFIGS_PATH)
    return [
        entry.stem
        for entry in p.iterdir()
        if entry.is_file() and entry.suffix == ".yml"
    ]


def _read_config(dashboard_id: str) -> Dict:
    return _read_config_file(f"{dashboard_id}.yml")


def _read_config_file(config_filename: str) -> Dict:
    file_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(file_dir, CONFIGS_PATH, config_filename)
    with open(config_path, "r", encoding="utf-8") as config_stream:
        return yaml.safe_load(config_stream)


def register_pages():
    blocked_ids = _get_blocked_ids()
    dashboard_ids = _get_dashboard_ids()
    for dashboard_id in dashboard_ids:
        if dashboard_id in blocked_ids:
            LOG.info(f"Dashboard '{dashboard_id}' is blocked, will not add")
            continue
        LOG.debug(f"Adding dashboard '{dashboard_id}'")
        dashboard_config = _read_config(dashboard_id)
        dashboard_layout = create_dashboard(dashboard_config)
        dashboard_title = dashboard_config.get("title", dashboard_id)
        if dashboard_title:
            register_page(
                dashboard_title, path=f"/{dashboard_id}", layout=dashboard_layout
            )
            LOG.debug(f"Added dashboard '{dashboard_title}'")
    LOG.info("Finished adding dashboards")
