from dash import Dash, dcc
from dash import html
from typing import Dict
from typing import List
import dash_bootstrap_components as dbc

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
FONT_COLOR = "#FFFFFF"
BACKGROUND_COLOR = "#161B21"


def create_dashboard_bootstrap(config: Dict) -> Dash:
    app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
            component_placements[sub_component_config['placement']]. \
                append((component, sub_component))

    main_children = {}
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
        if placement == "top" or placement == "bottom":
            main_children[placement] = dbc.Row(
                children=place_children
            )
        else:
            middle_children[placement] = dbc.Col(
                children=place_children
            )
    if len(middle_children) > 0:
        main_children['middle'] = dbc.Row(
            children=[middle_children['left'], middle_children['right']]
        )

    main = []
    if "top" in main_children:
        main.append(main_children["top"])
    if "middle" in main_children:
        main.append(main_children["middle"])
    if "bottom" in main_children:
        main.append(main_children["bottom"])

    sidebar = dbc.Col(
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
                dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                # Add more links as needed
            ],
            vertical="md",
        ),
        style={'background-color': BACKGROUND_COLOR},  # Change this to your preferred color
        width=2,  # Adjust width as needed
    )

    app.layout = dbc.Container(
        fluid=True,
        children=[
            dbc.Row(
                [
                    # sidebar,
                    # Rest of the layout
                    dbc.Col(
                        [
                            # Header
                            dbc.Row(
                                [
                                    dbc.Col(html.Img(src="assets/logo.png", style={'width': '200px'}), width=3),
                                    dbc.Col(html.H1("Georgia MAFS", className="text-center text-primary, mb-3"),
                                            width=6, style={'color': 'white'}),
                                ],
                                style={'backgroundColor': '#3B4758'}
                                # Add your color code here
                            ),
                            # Plots
                            *main,
                            # Footer
                            dbc.Row(
                                [
                                    dbc.Col(html.P("© 2024 Brockmann Consult GmbH. All rights reserved.",
                                                   className="text-center text-primary", style={'color': 'white'}),
                                            width=12),
                                ],
                                style={'backgroundColor': BACKGROUND_COLOR, 'padding': '10px'}
                                # Add your color code here
                            ),
                        ],
                        width=12,  # Adjust width as needed
                    ),
                ],
            ),
        ],
        style={'backgroundColor': BACKGROUND_COLOR, }
    )

    for component in components.values():
        component.register_callbacks(app, list(components.keys()))

    return app
