from dash import Dash, dcc
from dash import html
from typing import Dict
from typing import List
import dash_bootstrap_components as dbc

from doors_dashboards.components.constant import HEADER_BGCOLOR, CONTAINER_BGCOLOR, \
    FONT_COLOR
from doors_dashboards.components.scattermap import ScatterMapComponent
from doors_dashboards.components.meteogram import MeteogramComponent
from doors_dashboards.components.scatterplot import ScatterplotComponent
from doors_dashboards.components.selectcollection import SelectCollectionComponent
from doors_dashboards.components.timeseries import TimeSeriesComponent
from doors_dashboards.core.featurehandler import FeatureHandler

_COMPONENTS = {
    'scattermap': ScatterMapComponent,
    'meteogram': MeteogramComponent,
    'timeplots': TimeSeriesComponent,
    'scatterplot': ScatterplotComponent,
    'selectcollection': SelectCollectionComponent
}


def create_dashboard(config: Dict) -> Dash:
    dashboard_id = config.get("id")
    dashboard_title = config.get("title")
    app = Dash(__name__, suppress_callback_exceptions=True,
               external_stylesheets=[dbc.themes.BOOTSTRAP],
               title=dashboard_title
               )

    components = {}
    component_placements = dict(
        top=[],
        left=[],
        right=[],
        bottom=[]
    )

    feature_handler = FeatureHandler(config.get("features"), config.get("eez"))

    for component, component_dict in config.get("components", []).items():
        components[component] = _COMPONENTS[component]()
        components[component].set_feature_handler(feature_handler)
        for sub_component, sub_component_config in component_dict.items():
            component_placements[sub_component_config['placement']]. \
                append((component, sub_component))

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
            sub_component_params = config.get("components", {}). \
                get(main_component, {}).get(sub_component)
            component_div = components[main_component].get(
                sub_component, sub_component, sub_component_params
            )
            place_children.append(component_div)
        if placement == "top":
            top_children[placement] = place_children
        if placement == "bottom":
            main_children[placement] = dbc.Row(
                children=place_children
            )
        else:
            middle_children[placement] = dbc.Col(
                children=place_children
            )
    if len(middle_children) > 0:
        if "right" not in middle_children:
            main_children['middle'] = dbc.Row(
                [
                    middle_children['left']
                ]
            )
        elif "left" not in middle_children:
            main_children['middle'] = dbc.Row(
                [
                    middle_children['right']
                ]
            )
        else:
            main_children['middle'] = dbc.Row(
                [
                    dbc.Col(middle_children['left'], width="50%",
                            className='col-lg-6', style={'margin-top': '0px',
                                                         'margin-left': '4px'}),
                    dbc.Col(middle_children['right'], width="50%",
                            className='col-lg-6', style={'margin-top': '2px',
                                                         'margin-left': '-10px'})
                ]
            )

    main = []
    if "middle" in main_children:
        main.append(main_children["middle"])
    if "bottom" in main_children:
        main.append(main_children["bottom"])

    app.layout = html.Div([
        dcc.Store(id='general'),
        dcc.Store(id='collection_selector'),
        dcc.Store(id='group_selector'),
        dcc.Store(id="variable_selector"),
        # Header
        dbc.Row(
            [
                dbc.Col(html.Img(src="assets/logo.png",
                                 style={'width': '200px',
                                        'paddingTop': '5px',
                                        'text-wrap': 'nowrap'}),
                        width=3),
                dbc.Col(html.H1(dashboard_title,
                                className="text-center "
                                          "text-primary, mb-4"),
                        width=3, style={'color': FONT_COLOR,
                                        'paddingTop': '5px'}),
                dbc.Col(top_children["top"], width=6,
                        style={'marginTop': '-15px'}),
            ],
            style={'backgroundColor': HEADER_BGCOLOR}
        ),
        # Plots
        *main,
        # Footer
        dbc.Row(
            [
                dbc.Col(html.P(
                    "© 2024 Brockmann Consult GmbH. All rights reserved.",
                    className="text-center "
                              "text-primary",
                    style={'color': FONT_COLOR}),
                    width=12),
            ],
            style={'backgroundColor': CONTAINER_BGCOLOR,
                   'padding': '10px'}
        ),
    ], style={'backgroundColor': CONTAINER_BGCOLOR,
              'width': '100vw',
              'height': '100vh',
              'overflow': 'hidden',
              })

    for component in components.values():
        component.register_callbacks(app, list(components.keys()))

    return app
