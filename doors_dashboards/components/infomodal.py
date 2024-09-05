from dash import dcc
import dash_bootstrap_components as dbc
import os

from doors_dashboards.components.modal import create_modal


def create_info_modal(dashboard_id: str, dash_description: str):
    info_modal = create_modal(
        modal_id=f"{dashboard_id}-info",
        title="Info",
        content=dash_description,
        font_size="small"
    )
    return info_modal
