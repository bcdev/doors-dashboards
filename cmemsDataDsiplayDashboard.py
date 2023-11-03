import dash
import plotly.graph_objs as go
from dash import html, dcc
import dash_bootstrap_components as dbc

# Create a Dash app
app = dash.Dash(__name__)

# The URL of the ECMWF
ecmwfurl = "https://charts.ecmwf.int/opencharts-api/v1/products/opencharts_meteogram"
scale_factor = 0.5
image_url = 'https://charts.ecmwf.int/content/20231103081456-124b11b5e5a4ba9aa1a1d6a5dfc077f7be2c8648.png'
# Define the parameters for the ECMWF request
params = {
    "format": "png",
    "base_time": "2023-11-03T00%3A00%3A00Z",
    "epsgram": "classical_wave",
    "lon": "28.75",
    "lat": "44",
}





fig1 = go.Figure(go.Scattermapbox(), layout=dict(width=1000, height=700))
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
    html.Img(src='https://charts.ecmwf.int/content/20231103081456-124b11b5e5a4ba9aa1a1d6a5dfc077f7be2c8648.png')
],style={'display': 'flex', 'flex-direction': 'row'})

#get_ecmwf_data()

if __name__ == '__main__':
    app.run_server(debug=True)
