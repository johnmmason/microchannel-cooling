import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from gui.dash_template import new_app
from model.naive_model import MicroChannelCooler, Geometry
from model.fluids import water


def make_naive_app(server, prefix):

    app = new_app(server, prefix, centered='center')
    app.title = "Naive Model"
    app.version = 0.1
    # don't use H2 - that is reserved for dropdowns in Flask right now
    app.layout = html.Div([
        html.H1("Microchannel Cooling, Naive Method"),
        dbc.Row([
            dbc.Col([
                html.Div(["Length (m):", dcc.Input(id='length', value='0.1', type='text')]),
                html.Div(["Width (um):", dcc.Input(id='width', value='100', type='text')]),
                html.Div(["Depth (um):", dcc.Input(id='depth-from', value='10', type='text'),
                        " to ", dcc.Input(id='depth-to', value='50', type='text')]),
                html.Div(["Inlet Temperature (C):", dcc.Input(id='temp-inlet', value='20', type='text')]),
                html.Div(["Wall Temperature (C):", dcc.Input(id='temp-wall', value='100', type='text')]),
                html.Div(["Flow Rate (uL/min):", dcc.Input(id='flow-rate', value='100', type='text')]),
                ], style={'width': '20vw'}),
            dbc.Col([
                html.Div([dcc.Graph(id='plot')], style={'width': '70vw', 'min-width': '700px'}),
                ]),
        ]),
    ])

    @app.callback(
        Output(component_id='plot', component_property='figure'),
        Input('length','value'),
        Input('width','value'),
        Input('depth-from','value'),
        Input('depth-to','value'),
        Input('temp-inlet','value'),
        Input('temp-wall','value'),
        Input('flow-rate', 'value')
    )
    def update_output_div(length, width, depth_from, depth_to, temp_inlet, temp_wall, flow_rate):

        try:
            L = float(length) # length of microchannel [m]
            W = float(width) * 1e-6 # width of microchannel [m]
            
            T_in = float(temp_inlet)  + 273 # temperature of inlet [K]
            T_w = float(temp_wall) + 273 # temperature of wall [K]
            Q = float(flow_rate) # flow rate [uL/min]m]

            D_low = float(depth_from)
            D_high = float(depth_to)

            assert D_low < D_high
            D = np.arange( D_low, D_high, 1 ) * 1e-6 #depth of microchannel [m]
        except:
            raise PreventUpdate

        geom = Geometry(L, W, D)
        cooler = MicroChannelCooler(geom, water, T_in, T_w, Q)
        q, dP, T_out = cooler.solve()

        fig = make_subplots(rows=1, cols=2, column_widths=[.5, .5])

        fig.add_trace(row=1, col=1, trace=go.Scatter(x=D, y=q*1e-4))
        fig.add_trace(row=1, col=2, trace=go.Scatter(x=D, y=dP*0.000145038))

        fig.update_xaxes(title_text="Channel Depth (m)", row=1, col=1)
        fig.update_xaxes(title_text="Channel Depth (m)", row=1, col=2)
        fig.update_yaxes(title_text="Heat Flux (W/cm2)", row=1, col=1)
        fig.update_yaxes(title_text="Backpressure (psi)", row=1, col=2)

        fig.update_layout(height=600, showlegend=False)
        
        return fig

    return app.server
