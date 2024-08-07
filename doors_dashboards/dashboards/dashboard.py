from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from typing import Dict

from doors_dashboards.components.constant import FONT_COLOR
from doors_dashboards.components.meteogram import MeteogramComponent
from doors_dashboards.components.scattermap import ScatterMapComponent
from doors_dashboards.components.scatterplot import ScatterplotComponent
from doors_dashboards.components.selectcollection import SelectCollectionComponent
from doors_dashboards.components.timeseries import TimeSeriesComponent
from doors_dashboards.core.featurehandler import FeatureHandler

_COMPONENTS = {
    "scattermap": ScatterMapComponent,
    "meteogram": MeteogramComponent,
    "timeplots": TimeSeriesComponent,
    "scatterplot": ScatterplotComponent,
    "selectcollection": SelectCollectionComponent,
}


def create_dashboard(config: Dict) -> html.Div:
    dashboard_id = config.get("id")
    dashboard_title = config.get("title")
    store_ids = {
        "general": f"{dashboard_id}-general",
        "collection_selector": f"{dashboard_id}-collection_selector",
        "group_selector": f"{dashboard_id}-group_selector",
        "variable_selector": f"{dashboard_id}-variable_selector",
    }
    components = {}
    component_placements = dict(top=[], left=[], right=[], bottom=[])

    feature_handler = FeatureHandler(config.get("features"), config.get("eez"))

    for component, component_dict in config.get("components", dict()).items():
        components[component] = _COMPONENTS[component](dashboard_id)
        components[component].set_feature_handler(feature_handler)
        for sub_component, sub_component_config in component_dict.items():
            component_placements[sub_component_config["placement"]].append(
                (component, sub_component)
            )

    main_children = {}
    top_children = {}
    middle_children = {}
    for placement, components_at_placement in component_placements.items():
        if not components_at_placement:
            continue
        place_children = []
        for component_at_placement in components_at_placement:
            main_component = component_at_placement[0]
            sub_component = component_at_placement[1]
            sub_component_params = (
                config.get("components", {}).get(main_component, {}).get(sub_component)
            )
            component_div = components[main_component].get(
                sub_component, sub_component, sub_component_params
            )
            place_children.append(component_div)
        if placement == "top":
            top_children[placement] = dbc.Col(place_children, className="col m-1")
        if placement == "bottom":
            main_children[placement] = dbc.Row(children=place_children)
        else:
            middle_children[placement] = dbc.Col(children=place_children)
    if len(middle_children) > 0:
        if "right" not in middle_children:
            main_children["middle"] = dbc.Row(
                [middle_children["left"]],
            )
        elif "left" not in middle_children:
            main_children["middle"] = dbc.Row(
                [
                    middle_children["right"],
                ],
            )
        else:
            main_children["middle"] = dbc.Row(
                [
                    dbc.Col(middle_children["left"], className="col-6 px-1"),
                    dbc.Col(middle_children["right"], className="col-6 px-1"),
                ],
                style={"margin": "0"},
            )

    main = []
    if "middle" in main_children:
        main.append(main_children["middle"])
    if "bottom" in main_children:
        main.append(main_children["bottom"])

    layout = html.Div(
        [
            dcc.Store(id=store_ids["general"]),
            dcc.Store(id=store_ids["collection_selector"]),
            dcc.Store(id=store_ids["group_selector"]),
            dcc.Store(id=store_ids["variable_selector"]),
            dbc.Row(
                [
                    top_children["top"],
                    dbc.Col(
                        html.H1(dashboard_title),
                        style={"color": FONT_COLOR},
                        className="col m-1",
                    ),
                ],
                style={"height": "60px", "margin-top": "-3px"},
            ),
            # Plots
            *main,
        ]
    )

    for component in components.values():
        component.register_callbacks(list(components.keys()), dashboard_id)

    return layout
