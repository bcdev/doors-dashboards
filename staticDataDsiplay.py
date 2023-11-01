import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Sample wind wave data
data = {
    'Region': ['Region A', 'Region B', 'Region C', 'Region D'],
    'Wind Waves': [30, 25, 35, 20]
}
df = pd.DataFrame(data)

# Sample map data
map_data = {
    'Region': ['Region A', 'Region B', 'Region C', 'Region D'],
    'Latitude': [40, 35, 30, 25],
    'Longitude': [-120, -110, -100, -90],
    'Wind Waves': [30, 25, 35, 20]  # Adding Wind Waves data to the map data
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

    # Create the map with wind waves displayed using marker size
    map_figure = px.scatter_geo(
        filtered_map_data,
        lat='Latitude',
        lon='Longitude',
        text='Region',
        size='Wind Waves',  # Use wind waves data to set marker size
        projection='natural earth',
        title='Wind Waves on Map',
        size_max=20,  # Adjust the marker size as needed
        labels={'Wind Waves': 'Wind Waves'},
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
