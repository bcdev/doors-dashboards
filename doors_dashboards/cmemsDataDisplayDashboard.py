import dash
import plotly.graph_objs as go
from dash import html, dcc
import requests

# Create a Dash app
app = dash.Dash(__name__)

# The URL of the ECMWF
ecmwfurl = "https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram/"
scale_factor = 0.5
image_url = ''
# Define the parameters for the ECMWF request
headers = {"accept": "application/json"}
params = {
    "format": "png",
    "base_time": "2023-11-08T00:00:00Z",
    "epsgram": "classical_wave",
    "lon": "28",
    "lat": "42.6",
}
def get_ecmwf_data():
    response = requests.get(ecmwfurl, params=params, headers=headers)
    print(requests)
    if response.status_code != 200:
        return ecmwfurl
    else:
        response_data = response.json()
        image_url = response_data["data"]["link"]["href"]
        return image_url
        #print(response_data)


point_lat = 42.6
point_lon = 28

#get_ecmwf_data()

fig1 = go.Figure(go.Scattermapbox(lat=[point_lat],
    lon=[point_lon],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=9,color='blue'
    ),
    text='Bulgarian Coastline',))
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
        dcc.Graph(
            id='cmems-grph',
            figure=fig1
        ),
    html.Img(src=get_ecmwf_data())
],style={'display': 'flex', 'flex-direction': 'row', 'width': '100%', 'height': '100vh'})



if __name__ == '__main__':
    app.run_server(debug=True)
