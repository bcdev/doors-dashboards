from dash import html
from dash import Dash

from doors_dashboards.core.geodbaccess import get_points_from_geodb
from doors_dashboards.components.scattermap import ScatterMapComponent

DASHBOARD_ID = 'bulgarian_optical_data'


def _create_app() -> Dash:
    app = Dash(__name__)

    points = get_points_from_geodb(
        'bio-optical-data-K12_2019', 'io-bas',
        variables=['chl-a [mg/m3]', 'temperature [°c]', 'salinity [psu]',
                   'secchi disk [m]']
    )

    scattermap = ScatterMapComponent().get(DASHBOARD_ID, points)

    app.layout = html.Div(
        [
            html.Div(
                scattermap,
                style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'width': '100vh',
                    'height': '1000px',
                    'alignItems': 'center',
                }
            )
        ],
        style={
            'display': 'flex',
            'flexDirection': 'row',
            'width': '100%',
            'height': '100vh'
        }
    )
    return app


if __name__ == '__main__':
    app = _create_app()
    app.run_server(debug=True)
