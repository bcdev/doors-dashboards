from dash import dcc, callback, Output, Input, State
from dash import html
import dash_bootstrap_components as dbc
from typing import Dict, List

from doors_dashboards.components.constant import FONT_COLOR
from doors_dashboards.components.meteogram import MeteogramComponent
from doors_dashboards.components.scattermap import ScatterMapComponent
from doors_dashboards.components.scatterplot import ScatterplotComponent
from doors_dashboards.components.selectcollection import SelectCollectionComponent
from doors_dashboards.components.timeseries import TimeSeriesComponent
from doors_dashboards.core.featurehandler import FeatureHandler
import doors_dashboards.components.infomodal as info_modal

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
    dashboard_description = config.get("description")
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
            dcc.Interval(id=f"{dashboard_id}-interval", interval=1 * 1000,
                         n_intervals=0),
            dbc.Row(
                [
                    top_children["top"],
                    dbc.Col(
                        html.H1(dashboard_title),
                        style={"color": FONT_COLOR},
                        className="col m-1",
                    ),
                    dbc.Col(html.I(
                        className="fa fa-info-circle",
                        id=f"{dashboard_id}_info_open",
                        n_clicks=0,
                        title="Info",
                        style={
                            "cursor": "pointer",
                            "color": "white",
                        },
                    ), width="auto", className="m-1",
                    ),
                ],
                className="d-flex justify-content-between align-items-center",
                style={"height": "60px", "margin-top": "-3px"},
            ),
            # Plots
            *main,
            info_modal.create_info_modal(dashboard_id, dashboard_description,
                                         dashboard_title)
        ]
    )

    @callback(
        Output(f"modal-{dashboard_id}-info", "is_open"),
        [Input(f"{dashboard_id}_info_open", "n_clicks"),
         Input(f"close-{dashboard_id}-info", "n_clicks")],
        [State(f"modal-{dashboard_id}-info", "is_open")],
    )
    def toggle_info_modal(open_click, close_click, is_open):
        if open_click or close_click:
            return not is_open
        return is_open

    @callback(
        Output("none", "children",allow_duplicate=True),
        [Input(f"{dashboard_id}-interval", "n_intervals")],
        prevent_initial_call=True
    )
    def get_new_data(interval):
        collections = feature_handler.get_collections()
        for collection in collections:
            feature_handler.delete_df(collection)
        #for collection in collections:
        #feature_handler.get_df(collection)

    for component in components.values():
        component.register_callbacks(list(components.keys()), dashboard_id)

    return layout
