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

from typing import List

import doors_dashboards.dashboards as db

_AVAILABLE_DASHBOARDS = \
    {
        "Bulgaria Ports": db.bg1_cdb,
        "Bulgaria GeoDB": db.bg2_cdb,
        "Romania GeoDB": db.ro1_cdb,
        "Romania Meteograms": db.ro2_cdb,
    }
_SUPPORTED_MODES=[None, 'jupyterlab', 'tab']


def list_dashboards() -> List[str]:
    return list(_AVAILABLE_DASHBOARDS.keys())


def start_dashboard(dashboard_name: str, mode: str = 'jupyterlab'):
    if dashboard_name not in list_dashboards():
        available_dashboards = ", ".join(list_dashboards())
        raise ValueError(
            f"Dashboard '{dashboard_name}' not one of {available_dashboards}"
        )
    if mode not in _SUPPORTED_MODES:
        available_modes = ", ".join(_SUPPORTED_MODES)
        raise ValueError(
            f"Mode '{mode}' not one of {available_modes}"
        )
    dashboard = _AVAILABLE_DASHBOARDS.get(dashboard_name)()
    dashboard.run(jupyter_mode=mode)
