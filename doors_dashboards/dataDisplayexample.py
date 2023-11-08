import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os
from xcube.core.store import find_data_store_extensions
from xcube.core.store import get_data_store_params_schema
from xcube.core.store import new_data_store
from IPython.display import JSON

# Sample wind wave data
os.environ["CMEMS_USERNAME"] = "rmotwani"
os.environ["CMEMS_PASSWORD"] = "Krishna@2215"

get_data_store_params_schema('cmems')
store = new_data_store('cmems')
JSON(store.list_data_ids())
store.describe_data('cmems_mod_blk_wav_anfc_2.5km_PT1H-i')




data = {
    'Region': ['Region A', 'Region B', 'Region C', 'Region D'],
    'Wind Waves': [30, 25, 35, 20]
}
df = pd.DataFrame(data)

# Sample map data
map_data = {
    'Region': ['Region A', 'Region B', 'Region C', 'Region D'],
    'Latitude': [40, 35, 30, 25],
    'Longitude': [-120, -110, -100, -90]
}
map_df = pd.DataFrame(map_data)

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Wind Waves Dashboard"),
    dcc.Dropdown(
        id='dropdown-selection',
        options=[{'label': region, 'value': region} for region in df['Region']],
        value='Region A'
    ),
    dcc.Graph(id='map-graph'),
    dcc.Graph(id='wind-wave-graph'),

])


# Define callback to update map and wind wave graph
@app.callback(
    [Output('map-graph', 'figure'),
     Output('wind-wave-graph', 'figure')],
    [Input('dropdown-selection', 'value')]
)
def update_map_and_wind_wave_graph(selected_region):
    # Filter the map data based on the selected region
    filtered_map_data = map_df[map_df['Region'] == selected_region]

    map_figure = px.scatter_geo(
        filtered_map_data,
        lat='Latitude',
        lon='Longitude',
        text='Region',
        projection='natural earth',
        title='Region-wise Wind Waves',
    )

    wind_wave_figure = px.bar(
        df,
        x='Region',
        y='Wind Waves',
        title='Wind Waves by Region',
    )

    return map_figure, wind_wave_figure


if __name__ == '__main__':
    app.run_server(debug=True)
