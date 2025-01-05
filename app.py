import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
from chaos_game import chaos_game_triangle
from critexp import solve_for_d
import urllib
from dash import dash_table
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Add URL component at the top
    html.Div([
        html.H1("Chaos Game Triangle",style={'textAlign': 'center'}),
        # Add the input components
        dcc.Input(id='num-points-input', type='number', value=10000, placeholder="Number of points"),
        dcc.Input(id='p1-input', type='number', value=0.33, step=0.01, placeholder="p1"),
        dcc.Input(id='p2-input', type='number', value=0.33, step=0.01, placeholder="p2"),
        dcc.Input(id='r1-input', type='number', value=1/2, step=0.01, placeholder="r1"),
        dcc.Input(id='r2-input', type='number', value=1/2, step=0.01, placeholder="r2"),
        dcc.Input(id='r3-input', type='number', value=1/2, step=0.01, placeholder="r3"),
        # Add the update button
        html.Button('Update', id='update-button', n_clicks=0),
        html.Button('Open in New Tab', id='new-tab-button', n_clicks=0),
        # Add a label for the current parameter set
        html.Div(id='parameter-label'),
        dcc.Graph(id='point-cloud-animation',style={
                    'height': 'calc(100vh - 200px)',  # Responsive height
                    'minHeight': '400px'              # Minimum height
                }),
        html.Div(id='diagnostic-output', style={'whiteSpace': 'pre-line'}),
        dcc.Store(id='current-params'),
        # Store for bookmarked states
        dcc.Store(id='bookmarked-states', data=[]),
        html.Div(id='new-tab-dummy', style={'display': 'none'})
        ],
        style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '20px',
            'boxSizing': 'border-box'
        })], style = {
        'backgroundColor': '#f0f5f9',  # Or any color scheme
        'minHeight': '100vh'
        })

@app.callback(
    Output('point-cloud-animation', 'figure'),
    Output('diagnostic-output', 'children'),
    Output('parameter-label', 'children'),
    Output('current-params', 'data'), 
    Input('update-button', 'n_clicks'),
    Input('url', 'search'),  # Get URL query string
    State('num-points-input', 'value'),
    State('p1-input', 'value'),
    State('p2-input', 'value'),
    State('r1-input', 'value'),
    State('r2-input', 'value'),
    State('r3-input', 'value')
)
def update_figure(n_clicks, url_search,num_points, p1, p2, r1, r2, r3):
    if url_search:
        from urllib.parse import parse_qs
        params = parse_qs(url_search.replace('?', ''))
        # Use URL parameters if they exist, otherwise use input values
        num_points = float(params.get('num_points', [num_points])[0])
        p1 = float(params.get('p1', [p1])[0])
        p2 = float(params.get('p2', [p2])[0])
        r1 = float(params.get('r1', [r1])[0])
        r2 = float(params.get('r2', [r2])[0])
        r3 = float(params.get('r3', [r3])[0])
    params = {
        'num_points': num_points,
        'p1': p1, 'p2': p2,
        'r1': r1, 'r2': r2, 'r3': r3
    }
    
    fig, fd = generate_figure(params)
    fractal_dimension = solve_for_d(r1, r2, r3)
    diagnostic_text = f"Box dimension estimate {fd:.4f}"
    

    # Then modify the parameter label creation in your update_figure callback:
    param_label = html.Div([
    html.H3("Current Parameters"),
    dash_table.DataTable(
        id='param-table',
        columns=[
            {'name': 'Parameter', 'id': 'param'},
            {'name': 'Value', 'id': 'value'}
        ],
        data=[
            {'param': 'N points', 'value': f"{num_points}"},
            {'param': 'p₁', 'value': f"{p1:.3f}"},
            {'param': 'p₂', 'value': f"{p2:.3f}"},
            {'param': 'r₁', 'value': f"{r1:.3f}"},
            {'param': 'r₂', 'value': f"{r2:.3f}"},
            {'param': 'r₃', 'value': f"{r3:.3f}"}
        ],
        style_table={'width': '300px'},
        style_cell={
            'textAlign': 'center',
            'padding': '10px'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    ),
    html.Div([
        dcc.Markdown(
            f'**Critical exponent:** *d* = {fractal_dimension:.4f}',
            mathjax=True
            )
        ], style={'marginTop': '10px'})
    ])
        
    return fig, diagnostic_text, param_label, params

# Add bookmark functionality
@app.callback(
    Output('bookmarked-states', 'data'),
    Input('bookmark-button', 'n_clicks'),
    State('current-params', 'data'),
    State('bookmarked-states', 'data'),
    prevent_initial_call=True
)
def add_bookmark(n_clicks, current_params, existing_bookmarks):
    if n_clicks is None or current_params is None:
        raise PreventUpdate
    
    # Initialize existing_bookmarks if it's None
    if existing_bookmarks is None:
        existing_bookmarks = []
    
    # Add timestamp to current parameters
    from datetime import datetime
    bookmark_params = current_params.copy()  # Make a copy to avoid modifying the original
    bookmark_params['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add to bookmarks
    existing_bookmarks.append(bookmark_params)
    return existing_bookmarks

# Add comparison view
def create_comparison_layout(params1, params2):
    return html.Div([
        html.H2("Parameter Comparison"),
        html.Div([
            html.Div([
                create_single_view(params1),
            ], style={'width': '50%', 'display': 'inline-block'}),
            html.Div([
                create_single_view(params2),
            ], style={'width': '50%', 'display': 'inline-block'})
        ])
    ])

def generate_figure(params):
    """Generate a figure from the given parameters"""
    # Extract parameters
    num_points = params['num_points']
    p1 = params['p1']
    p2 = params['p2']
    r1 = params['r1']
    r2 = params['r2']
    r3 = params['r3']
    
    # Generate data
    thedata, fd = chaos_game_triangle(num_points, p1, p2, r1, r2, r3)
    xarray = thedata[:, 1]
    yarray = thedata[:, 2]
    times = thedata[:, 0]
    
    num_frames = 50  # Move this to a variable since we'll use it multiple times
    
    # Create figure
    fig = go.Figure(
        data=[go.Scatter(
            x=[], 
            y=[], 
            mode='markers',
            marker=dict(
                size=600/np.sqrt(num_points),
                opacity=0.6
            )
        )],
        layout=go.Layout(
            xaxis=dict(range=[-0.1, 1.1]),
            yaxis=dict(range=[-0.1, 1.1]),
            # Add slider to show animation progress
            sliders=[{
                'currentvalue': {"prefix": "Frame: "},
                'pad': {"t": 50},
                'steps': [
                    {
                        "args": [[f"frame{k}"], {
                            "frame": {"duration": 0},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }],
                        "label": f"{k}/{num_frames}",
                        "method": "animate"
                    } 
                    for k in range(num_frames)
                ]
            }],
            updatemenus=[dict(
                type="buttons",
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None, {
                             "frame": {"duration": 50, "redraw": True},
                             "fromcurrent": True,
                         }]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None], {
                             "frame": {"duration": 0, "redraw": False},
                             "mode": "immediate",
                             "transition": {"duration": 0}
                         }])
                ],
                direction="left",
                pad={"r": 10, "t": 10},
                showactive=False,
                x=0.1,
                xanchor="right",
                y=1.1,
                yanchor="top"
            )]
        )
    )
    
    frames = [
        go.Frame(
            data=[go.Scatter(
                x=xarray[times < t],
                y=yarray[times < t],
                mode='markers',
                marker=dict(
                    size=600/np.sqrt(num_points),
                    opacity=0.6
                )
            )],
            name=f'frame{i}'  # Changed to match slider frame names
        )
        for i, t in enumerate(np.linspace(np.min(times), np.max(times), num_frames))
    ]

    fig.frames = frames
    return fig, fd

def create_single_view(params):
    return html.Div([
        html.H3("Parameters:"),
        html.P(f"Points: {params['num_points']}"),
        html.P(f"p1: {params['p1']:.3f}, p2: {params['p2']:.3f}"),
        html.P(f"r1: {params['r1']:.3f}, r2: {params['r2']:.3f}, r3: {params['r3']:.3f}"),
        dcc.Graph(id={'type': 'dynamic-graph', 'index': id(params)},
                 figure=generate_figure(params))
    ])

# Add UI elements for bookmarks and comparison
app.layout.children.extend([
    html.Button('Bookmark Current State', id='bookmark-button', n_clicks=0),
    html.Div([
        html.H3("Bookmarked States"),
        html.Div(id='bookmark-list')
    ]),
    html.Div(id='comparison-view')
])

@app.callback(
    Output('bookmark-list', 'children'),
    Input('bookmarked-states', 'data')
)
def update_bookmark_list(bookmarks):
    if not bookmarks:
        return "No bookmarks yet"
    
    return html.Ul([
        html.Li([
            f"State from {bookmark['timestamp']}: ",
            html.Button('Load', id={'type': 'load-bookmark', 'index': i}),
            html.Button('Compare', id={'type': 'compare-bookmark', 'index': i})
        ]) for i, bookmark in enumerate(bookmarks)
    ])
if __name__ == '__main__':
    app.run_server(debug=True)
