import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
from chaos_game import chaos_game_triangle
from critexp import solve_for_d
import dash_daq as daq

# def generate_points(max_time, num_points):
#     times = np.random.uniform(0, max_time, num_points)
#     x = np.random.randn(num_points)
#     y = np.random.randn(num_points)
#     z = np.random.randn(num_points)
#     return x, y, z, times

# max_time = 10
# num_points = 1000
# x, y, z, times = generate_points(max_time, num_points)


# thedata = chaos_game_triangle(100000)

# fig = go.Figure(
#     data=[go.Scatter(x=[], y=[], mode='markers')],
#     layout=go.Layout(
#         xaxis=dict(range=[-0.1,  1.1]),
#         yaxis=dict(range=[-0.1, 1.1]),
#         updatemenus=[dict(
#             type="buttons",
#             buttons=[dict(label="Play", method="animate", args=[None])]
#         )]
#     )
# )

# # ... (previous imports and data generation code)

# frames = [
#     go.Frame(
#         data=[go.Scatter(
#             x=thedata.x.loc[:t],
#             y=thedata.y.loc[:t],
#             mode='markers'
#         )],
#         name=f't={t:.1f}'
#     )
#     for t in np.linspace(thedata.index.min(), thedata.index.max(), 50)
# ]

# fig.frames = frames

# ... (rest of the Dash app code)

app = dash.Dash(__name__)
server = app.server

# app.layout = html.Div([
#     html.H1("Point Cloud Animation"),
#     dcc.Graph(id='point-cloud-animation', figure=fig)
# ])

app.layout = html.Div([
    html.H1("Chaos Game Triangle"),
    dcc.Input(id='num-points-input', type='number', value=100000, placeholder="Number of points"),
    #daq.PrecisionInput(id='p1-input',precision=2,value=1/3,label='p1',min=0, max=1),
    #daq.PrecisionInput(id='p2-input',precision=2,value=1/3,label='p2',min=0, max=1),
    dcc.Input(id='p1-input', type='number', value=0.33, step=0.01, placeholder="p1"),
    dcc.Input(id='p2-input', type='number', value=0.33, step=0.01, placeholder="p2"),
    dcc.Input(id='r1-input', type='number', value=1/2, step=0.01, placeholder="r1"),
    dcc.Input(id='r2-input', type='number', value=1/2, step=0.01, placeholder="r2"),
    dcc.Input(id='r3-input', type='number', value=1/2, step=0.01, placeholder="r3"),
    html.Button('Update', id='update-button', n_clicks=0),
    dcc.Graph(id='point-cloud-animation'),
    html.Div(id='diagnostic-output', style={'whiteSpace': 'pre-line'}),
])

@app.callback(
    Output('point-cloud-animation', 'figure'),
    Output('diagnostic-output', 'children'),
    Input('update-button', 'n_clicks'),
    State('num-points-input', 'value'),
    State('p1-input', 'value'),
    State('p2-input', 'value'),
    State('r1-input', 'value'),
    State('r2-input', 'value'),
    State('r3-input', 'value')
)
def update_figure(n_clicks, num_points, p1, p2, r1, r2, r3):
    thedata, fd = chaos_game_triangle(num_points, p1, p2, r1, r2, r3)
    xarray = thedata[:, 1]
    yarray = thedata[:, 2]
    times = thedata[:, 0]
    fractal_dimension = solve_for_d(r1, r2, r3)
    diagnostic_text = f"Critical exponent: {fractal_dimension:.4f}, fbox dimension estimate {fd:.4f}"

    fig = go.Figure(
        data=[go.Scatter(x=[], y=[], mode='markers')],
        layout=go.Layout(
            xaxis=dict(range=[-0.1,  1.1]),
            yaxis=dict(range=[-0.1, 1.1]),
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play", method="animate", args=[None])]
            )]
        )
    )
    
    frames = [
    go.Frame(
        data=[go.Scatter(
            x=xarray[times<t],
            y=yarray[times<t],
            mode='markers'
        )],
        name=f't={t:.1f}'
    )
for t in np.linspace(np.min(times), np.max(times), 50)
]

    fig.frames = frames
    # Create your figure here using thedata
    # ...

    return fig, diagnostic_text

if __name__ == '__main__':
    app.run_server(debug=True)
