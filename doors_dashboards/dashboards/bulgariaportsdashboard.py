from dash import html, Input, Output
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
METEROGRAM_ID = 'ecmwf-img'


def _create_app() -> Dash:
    app = Dash(__name__)

    scattermap = ScatterMapComponent().get(DASHBOARD_ID, BULGARIA_PORTS_POINTS)
    coastline_central = BULGARIA_PORTS_POINTS[0]
    marker_label_default = coastline_central[2]
    meteogram = MeteogramComponent().get(coastline_central[0], coastline_central[1])

    app.layout = html.Div(
        [scattermap,
         html.Div(
             id=METEROGRAM_ID,
             children=[
                 html.Label(
                     id='marker-label',
                     children=marker_label_default,
                     style={'textAlign': 'center', 'fontSize': '24px', 'fontWeight': 'bold', 'marginBottom': '10px'}
                 ),
                 meteogram
             ]
         )],
        style={
            'display': 'flex',
            'flexDirection': 'row',
            'width': '100%',
            'height': '100vh'
        }
    )

    @app.callback(Output('marker-label', 'children'),
                  Output(METEROGRAM_ID, 'children'),
                  Input(DASHBOARD_ID, 'clickData')
                  )
    def update_ecmwf_image(click_data):
        print(marker_label_default)
        if click_data is None:
            marker_label = marker_label_default
            return marker_label,meteogram
        else:
            marker_label = click_data['points'][0]['text']
            return marker_label, MeteogramComponent().get(click_data['points'][0]['lon'], click_data['points'][0]['lat'])

    return app


if __name__ == '__main__':
    app = _create_app()
    app.run_server(debug=True)
