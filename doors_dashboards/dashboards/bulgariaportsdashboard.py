from dash import html
from dash import Dash

from doors_dashboards.components.scattermap import ScatterMapComponent
from doors_dashboards.components.meteogram import MeteogramComponent

DASHBOARD_ID = 'bulgarian_ports'
BULGARIA_PORTS_POINTS = [
    (27.479, 42.486, 'Terminal East'),
    (27.47, 42.486, 'Terminal Bulk Cargoes'),
    (27.467, 42.48, 'Terminal 2A'),
    (27.457, 42.485, 'Terminal West'),
    (27.53, 42.45, 'Terminal Rosenets'),
    (27.728, 42.657, 'Terminal Nessebar'),
    (27.687, 42.42, 'Terminal Sozopol')
]


def _create_app() -> Dash:
    app = Dash(__name__)

    scattermap = ScatterMapComponent().get(DASHBOARD_ID, BULGARIA_PORTS_POINTS)
    coastline_central = BULGARIA_PORTS_POINTS[0]
    meteogram = MeteogramComponent().get(coastline_central[0], coastline_central[1])

    app.layout = html.Div(
        [scattermap, meteogram],
        style={
            'display': 'flex',
            'flex-direction': 'row',
            'width': '100%',
            'height': '100vh'
        }
    )

    return app


if __name__ == '__main__':
    app = _create_app()
    app.run_server(debug=True)
