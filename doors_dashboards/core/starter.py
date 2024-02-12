# The MIT License (MIT)
# Copyright (c) 2024 by Brockmann Consult
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import sys
import yaml
from typing import Dict
from typing import List
from waitress import serve

from doors_dashboards.dashboards.dashboard_bootstrap import create_dashboard_bootstrap

_CONFIGS_PATH = "../../configs"
_SUPPORTED_MODES=[None, 'jupyterlab', 'tab']


def _read_config(id: str) -> Dict:
    return _read_config_file(f"{id}.yml")


def _read_config_file(config_filename: str) -> Dict:
    config_path = os.path.join(_CONFIGS_PATH, config_filename)
    with open(config_path, "r", encoding="utf-8") as config_stream:
        return yaml.safe_load(config_stream)


def list_dashboards() -> List[str]:
    config_filenames = os.listdir(_CONFIGS_PATH)
    available_dashboards = []
    for config in config_filenames:
        if not config.endswith(".yml"):
            continue
        config = _read_config_file(config)
        available_dashboards.append(config.get("id"))
    return available_dashboards


def get_dashboard(dashboard_id: str):
    if dashboard_id not in list_dashboards():
        available_dashboards = ", ".join(list_dashboards())
        raise ValueError(
            f"Dashboard '{dashboard_id}' not one of {available_dashboards}"
        )
    if mode not in _SUPPORTED_MODES:
        available_modes = ", ".join(_SUPPORTED_MODES)
        raise ValueError(
            f"Mode '{mode}' not one of {available_modes}"
        )
    dashboard_config = _read_config(dashboard_id)
    return create_dashboard_bootstrap(dashboard_config)


def start_dashboard(dashboard_id: str, mode: str = 'jupyterlab'):
    dashboard = get_dashboard(dashboard_id)
    dashboard.run(jupyter_mode=mode)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise ValueError("Must pass at least dashboard id")
    if len(sys.argv) > 3:
        raise ValueError("Must pass not more than two parameters")
    dashboard_id = sys.argv[1]
    mode = None
    if len(sys.argv) == 3:
        # mode = sys.argv[2]
        # mode = sys.argv[2]
        dashboard = get_dashboard(dashboard_id)
        serve(dashboard.server, host="0.0.0.0", port=8787)
    else:
        start_dashboard(dashboard_id, mode)
