import requests
import plotly.graph_objs as go
import dash
from dash import html, dcc
import base64

# Create a Dash app
app = dash.Dash(__name__)

# The URL of the WMS service
url = "https://my.cmems-du.eu/thredds/wms/cmems_mod_blk_wav_my_2.5km_PT1H-i"

# Define the parameters for the WMS request
params = {
    "request": "GetMap",
    "service": "WMS",
    "VERSION": "1.3.0",
    "LAYERS": "VMDR_WW",
    "CRS": "EPSG:4326",
    "BBOX": "27,41.75,28.75,44",  # Corrected BBOX
    "WIDTH": "100",
    "HEIGHT": "100",
    "STYLES": "",  # You can specify styles if needed
    "FORMAT": "image/png"
}

# Send the HTTP GET request
response = requests.get(url, params=params)

if response.status_code == 200:
    imgsource = base64.b64encode(response.content).decode('utf-8')
    fig1 = go.Figure(go.Scattermapbox(), layout=dict(width=1000, height=700))
    mapboxt = 'YOUR_MAPBOX_TOKEN'  # Replace with your Mapbox token
    mapbox = dict(
        zoom=4.5,
        accesstoken=mapboxt,
        style='light',  # Set your preferred Mapbox style
        center=dict(lat=42.375, lon=27.875),  # Adjust center accordingly
        layers=[
            dict(
                source=imgsource,
                sourcetype="image",
                coordinates=[
                    [27, 41.75], [28.75, 41.75], [28.75, 44], [27, 44]
                ])
        ])

    fig1.update_layout(mapbox=mapbox)

    app.layout = html.Div([
        dcc.Graph(
            id='example-graph',
            figure=fig1
        )
    ])
else:
    print(f"Request failed with status code {response.status_code}")

if __name__ == '__main__':
    app.run_server(debug=True)
