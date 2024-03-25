import dash
from dash import dcc, html, Input, Output, State

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Store(id='store1', data={'value1': 10}),
    dcc.Store(id='store2', data={'value2': 20}),
    html.Button('Update Store 1', id='update-button_1', n_clicks=0),
    html.Button('Update Store 2', id='update-button_2', n_clicks=0),
    html.Div(id='output')
])


@app.callback(
    Output('store1', 'data'),
    Input('update-button_1', 'n_clicks'),
    State('store1', 'data')
)
def update_store_1(n_clicks, data1):
    if n_clicks > 0:
        # Update values in store1
        data1['value1'] += 1
    return data1


@app.callback(
    Output('store2', 'data'),
    Input('update-button_2', 'n_clicks'),
    State('store2', 'data')
)
def update_store_2(n_clicks, data2):
    if n_clicks > 0:
        # Update values in store2
        data2['value2'] += 1
    return data2


@app.callback(
    Output('output', 'children'),
    [Input('store1', 'data'), Input('store2', 'data')]
)
def update_output(data1, data2):
    total_value = data1['value1'] + data2['value2']
    return f'Total value: {total_value}'


if __name__ == '__main__':
    app.run_server(debug=True)