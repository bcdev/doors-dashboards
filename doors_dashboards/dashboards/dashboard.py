from dash import Dash
from dash import html
from dash_material_ui import FormLabel
from typing import Dict
from typing import List

from doors_dashboards.components.scattermap import ScatterMapComponent
from doors_dashboards.components.meteogram import MeteogramComponent
from doors_dashboards.components.timeseries import TimeSeriesComponent
from doors_dashboards.core.featurehandler import FeatureHandler

_COMPONENTS = {
    'scattermap': ScatterMapComponent,
    'meteogram': MeteogramComponent,
    'timeplots': TimeSeriesComponent
}
FONT_COLOR = "#cedce2"
BACKGROUND_COLOR = 'rgb(12, 80, 111)'

COLUMN_STYLE = {"flex": "1", 'paddingTop': '20px', 'height': '90%'}
ROW_STYLE = {'display': 'flex', "flex-direction": "row"}


def _get_style(placement: str, component_placements: Dict) -> Dict:
    if placement in ["top", "bottom"]:
        return ROW_STYLE
    style = COLUMN_STYLE.copy()
    if component_placements["right"] and component_placements["left"]:
        style["width"] = "50%"
    else:
        style["width"] = "100%"
    return style


def _order_main(main: Dict) -> List:
    res = []
    if "top" in main:
        res.append(main["top"])
    if "middle" in main:
        res.append(main["middle"])
    if "bottom" in main:
        res.append(main["bottom"])
    return res


def _order_middle(middle: Dict) -> List:
    res = []
    if "left" in middle:
        res.append(middle["left"])
    if "right" in middle:
        res.append(middle["right"])
    return res


def create_dashboard(config: Dict) -> Dash:
    app = Dash(__name__, suppress_callback_exceptions=True)

    components = {}
    component_placements = dict(
        top=[],
        left=[],
        right=[],
        bottom=[]
    )
    dashboard_id = config.get("id")
    dashboard_title = config.get("title")

    feature_handler = FeatureHandler(config.get("features"))

    for component, component_dict in config.get("components", []).items():
        components[component] = _COMPONENTS[component]()
        components[component].set_feature_handler(feature_handler)
        for sub_component, sub_component_config in component_dict.items():
            component_placements[sub_component_config['placement']].\
                append((component, sub_component))


    main_children = {}
    middle_children = {}
    for placement, components_at_placement in component_placements.items():
        if not components_at_placement:
            continue
        style = _get_style(placement, component_placements)
        place_children = []
        for component_at_placement in components_at_placement:
            main_component = component_at_placement[0]
            sub_component = component_at_placement[1]
            sub_component_params = config.get("components", {}).\
                get(main_component, {}).get(sub_component)
            component_div = components[main_component].get(
                sub_component, sub_component, sub_component_params
            )
            place_children.append(component_div)
        if placement == "top" or placement == "bottom":
            main_children[placement] = html.Div(
                style=style, children=place_children
            )
        else:
            middle_children[placement] = html.Div(
                style=style, children=place_children
            )
    if len(middle_children) > 0:
        middle = _order_middle(middle_children)
        main_children['middle'] = html.Div(
            style={
                'display': 'flex',
                'height': '80vh',
                "flex-direction": "row"
            },
            children=middle
        )
    main = _order_main(main_children)

    app.layout = html.Div(
        style={
            'height': '80vh',
        },
        children=[
            # Header
            html.Header(
                [
                    html.Img(src="assets/logo.png", style={'width': '200px'}),
                    FormLabel(dashboard_title,
                              style={'fontSize': '-webkit-xxx-large',
                                     'margin': '0 0 0 100px',
                                     'color': FONT_COLOR}
                              )
                ],
                style={
                    "display": "flex",
                    'backgroundColor': BACKGROUND_COLOR,
                    'padding': '15px',
                    "alignItems": "left",
                }
            ),
            # Main body
            html.Div(
                style={
                    'display': 'flex',
                    "flex-direction": "column"
                },
                children=main,
            ),
            # Footer
            html.Footer(
                style={
                    'backgroundColor': BACKGROUND_COLOR,
                    'color': FONT_COLOR,
                    'padding': '10px', 'position': 'fixed', 'bottom': '0',
                    'width': '100%',
                    'fontFamily': 'Roboto, Helvetica, Arial, sans-serif'
                },
                children=[
                    html.P(
                        '© 2024 Brockmann Consult GmbH. All rights reserved.'
                    ),
                ]
            ),
        ]
    )

    for component in components.values():
        component.register_callbacks(app, list(components.keys()))

    return app
