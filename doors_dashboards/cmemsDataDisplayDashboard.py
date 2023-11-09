import dash
import plotly.graph_objs as go
from dash import html, dcc
from dash.dependencies import Input, Output
import requests
from datetime import datetime

# Create a Dash app
app = dash.Dash(__name__)

# The URL of the ECMWF
ecmwfurl = "https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram/"
scale_factor = 0.5
image_url = ''
current_date = datetime.now().strftime("%Y-%m-%dT00:00:00Z")

# Define the parameters for the ECMWF request
headers = {"accept": "application/json"}

params = {
    "format": "png",
    "base_time": current_date,
    "epsgram": "classical_wave",
    "lon": "28",
    "lat": "42.6",
}

def get_ecmwf_data():
    response = requests.get(ecmwfurl, params=params, headers=headers)
    if response.status_code != 200:
        return ecmwfurl
    else:
        response_data = response.json()
        image_url = response_data["data"]["link"]["href"]
        return image_url

point_lat = [42.6, 42.525, 42.47, 42.655]
point_lon = [28, 27.7, 27.46, 27.725]

fig1 = go.Figure(go.Scattermapbox(lat=point_lat, lon=point_lon, mode='markers',
    marker=go.scattermapbox.Marker(size=9, color='blue'),
    text=['Bulgarian Coastline', 'Burgas Bay', 'Burgas Port', 'Passenger Terminal in Nessebar']))

mapboxt = 'pk.eyJ1Ijoicm1vdHdhbmkiLCJhIjoiY2xvNDVndHY2MDRlejJ4czIwa3QyYnk2bCJ9.g88Jq0lCZRcQda4eNPks2Q'
mapbox = dict(
    zoom=4.5,
    accesstoken=mapboxt,
    center=dict(lat=44, lon=28.75),
)

fig1.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                   legend=dict(x=0.01, y=0.05, traceorder="normal"),
                   mapbox_style="open-street-map"
                   )
fig1.update_layout(mapbox=mapbox)

app.layout = html.Div([
    html.Div('DOORS Dashboard', style={ 'padding': '20px','text-align': 'center','background': '#3093e3','color': 'white','font-size': '30px'}),
    html.Div([
        dcc.Graph(
            id='cmems-grph',
            figure=fig1,
            style={'margin-top': '30px'}
        ),
        html.Div(
            id='ecmwf-image',
            children=[
                html.Img(src=get_ecmwf_data())
            ]
        )
    ], style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'height': '100vh'})
])

@app.callback(
    Output('ecmwf-image', 'children'),
    Input('cmems-grph', 'clickData')
)
def update_ecmwf_image(click_data):
    if click_data is None:
        return [html.Img(src=get_ecmwf_data())]
    else:
        lat = click_data['points'][0]['lat']
        lon = click_data['points'][0]['lon']

        params["lat"] = str(lat)
        params["lon"] = str(lon)

        new_image_url = get_ecmwf_data()

        return [html.Img(src=new_image_url)]

if __name__ == '__main__':
    app.run_server(debug=True)
