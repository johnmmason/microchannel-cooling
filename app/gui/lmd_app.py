import json
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, ctx, MATCH, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from gui.dash_template import new_app
from model.naive_model import MicroChannelCooler, Geometry
from model.fluids import fluids, fluidoptions
from model.limits import test_input, test_single_input, microscale, kelvin, limits
from config import update_style
from model.func import funct, functoptions

def make_lmd_app(server, prefix):
    app = new_app(server, prefix, centered='center')
    app.title = "Lumped Mass Model"
    app.version = 0.1
    # don't use H2 - that is reserved for dropdowns in Flask right now
    app.layout = html.Div([
        html.H1("Microchannel Cooling, Lumped Mass Model", className='rh-align'),
        html.Div([
            html.Div([
                html.Div(id='err'),
                html.Br(),
                html.Div(["Fluid:",
                          dbc.Select(fluidoptions, placeholder="Water", value=0, id={'type': 'in', 'name': 'fluid'})],
                         className='input-box'),
                html.Div(["Length (m):",
                          dbc.Input(id={'type': 'in', 'name': 'L'}, value=limits['L']['init'], type='number')],
                         className='input-box'),
                html.Div(["Width (um):",
                          dbc.Input(id={'type': 'in', 'name': 'W'}, value=limits['W']['init'], type='number')],
                         className='input-box'),
                html.Div(["Depth (um) (start):",
                          dbc.Input(id={'type': 'in', 'name': 'H_from'}, value=limits['H']['min'], type='number')],
                         className='input-box'),
                html.Div(["Depth (um) (end):",
                          dbc.Input(id={'type': 'in', 'name': 'H_to'}, value=limits['H']['max'], type='number')],
                         className='input-box'),
                html.Div(["Inlet Temperature (C):",
                          dbc.Input(id={'type': 'in', 'name': 'T_in'}, value=limits['T_in']['init'], type='number')],
                         className='input-box'),
                html.Div(["Wall Temperature (C):",
                          dbc.Input(id={'type': 'in', 'name': 'T_w'}, value=limits['T_w']['init'], type='number')],
                         className='input-box'),
                html.Div(["Flow Rate (uL/min):",
                          dbc.Input(id={'type': 'in', 'name': 'Q'}, value=limits['Q']['init'], type='number')],
                         className='input-box'),
                html.Div(["Amplitude (W/cm^2):",
                          dbc.Input(id={'type': 'in', 'name': 'A'}, value=limits['A']['init'], type='number')],
                         className='input-box'),
                html.Div(["Functions:",
                          dbc.Select(functoptions, placeholder="Constant", value=0, id={'type': 'in', 'name': 'funct'})],
                         className='input-box'),                
            ], className='input'),
            html.Div(className='hspace'),
            html.Div([dcc.Graph(id='plot')], className='plot'),
        ], className='row'),
        html.Div(id='cancel_button_id', style={'display': 'none'}),  # workaround for dash errors.
    ])

    @app.callback(
         Output(component_id='plot', component_property='figure'),
         Input({'type': 'in', 'name': 'fluid'}, 'value'),
         Input({'type': 'in', 'name': 'L'}, 'value'),
         Input({'type': 'in', 'name': 'W'}, 'value'),
         Input({'type': 'in', 'name': 'H_from'}, 'value'),
         Input({'type': 'in', 'name': 'H_to'}, 'value'),
         Input({'type': 'in', 'name': 'T_in'}, 'value'),
         Input({'type': 'in', 'name': 'T_w'}, 'value'),
         Input({'type': 'in', 'name': 'Q'}, 'value'),
         Input({'type': 'in', 'name': 'A'}, 'value'),
         Input({'type': 'in', 'name': 'funct'}, 'value'),
    )
    def update_output_div(fluid, L, W, depth_from, depth_to, temp_inlet, temp_wall, flow_rate, funct):

        try:
            L = float(L)  # L of microchannel [m]
            W = float(W) * microscale  # W of microchannel [m]

            try:
                F = fluids[int(fluid)]
            except Exception as e:
                print(e)
                F = fluids[0]

            T_in = float(temp_inlet) + kelvin  # temperature of inlet [K]
            T_w = float(temp_wall) + kelvin  # temperature of wall [K]
            Q = float(flow_rate)  # flow rate [uL/min]m]

            H_low = float(depth_from)
            H_high = float(depth_to)

            assert H_low < H_high
            H = np.linspace(H_low, H_high, 500) * microscale  # depth of microchannel [m]
        except:
            raise PreventUpdate

        q = np.empty(len(H))
        dP = np.empty(len(H))
        T_out = np.empty(len(H))

        if funct == "Constant":
            heat_flux_functions = lambda x,y: 5.0
        
        elif funct == "Linear":
            heat_flux_functions = lambda x: 5.0*x
        
        elif funct == "Gaussian":
            heat_flux_functions = lambda x: gaussian(1., 0.5, 0.5, 1., 1.)
        

        for i in range(len(H)):
            geom = Geometry(L, W, H[i])
            cooler = MicroChannelCooler(T_in, T_w, Q, geom, F)
            q[i], dP[i], T_out[i] = cooler.solve()

        fig = make_subplots(rows=1, cols=3, column_widths=[.33, .33, .33])

        fig.add_trace(row=1, col=1, trace=go.Scatter(x=H, y=q))
        fig.add_trace(row=1, col=2, trace=go.Scatter(x=H, y=dP * 0.000145038))
        fig.add_trace(row=1, col=3, trace=go.Scatter(x=H, y=T_out - kelvin))

        fig.update_xaxes(title_text="Channel Depth (m)", row=1, col=1)
        fig.update_xaxes(title_text="Channel Depth (m)", row=1, col=2)
        fig.update_xaxes(title_text="Channel Depth (m)", row=1, col=3)
        fig.update_yaxes(title_text="Heat Flux (W/cm2)", row=1, col=1)
        fig.update_yaxes(title_text="Backpressure (psi)", row=1, col=2)
        fig.update_yaxes(title_text="Outlet Temperature (C)", row=1, col=3)

        RANGE_CONSTANT = 0.1

        # Fix for extremely small variations in heat flux

        q_range = (np.max(q) - np.min(q)) * RANGE_CONSTANT

        if q_range < 0.001: q_range = 0.01

        q_lower = np.min(q) - q_range
        q_upper = np.max(q) + q_range

        fig.update_layout(yaxis1=dict(range=[q_lower, q_upper]))

        # Fix for extremely small variations in outlet temperature

        T_range = (np.max(T_out) - np.min(T_out)) * RANGE_CONSTANT

        if T_range < 0.01: T_range = 0.01

        T_lower = np.min(T_out) - T_range - kelvin
        T_upper = np.max(T_out) + T_range - kelvin

        fig.update_layout(yaxis3=dict(range=[T_lower, T_upper]))

        fig.update_layout(height=600, showlegend=False)
        update_style(fig)

        return fig

    @app.callback(
        Output('err', 'children'),
        inputs=dict(
            fluid=Input({'type': 'in', 'name': 'fluid'}, 'value'),
            L=Input({'type': 'in', 'name': 'L'}, 'value'),
            W=Input({'type': 'in', 'name': 'W'}, 'value'),
            H_from=Input({'type': 'in', 'name': 'H_from'}, 'value'),
            H_to=Input({'type': 'in', 'name': 'H_to'}, 'value'),
            T_in=Input({'type': 'in', 'name': 'T_in'}, 'value'),
            T_w=Input({'type': 'in', 'name': 'T_w'}, 'value'),
            Q=Input({'type': 'in', 'name': 'Q'}, 'value'),
            A=Input({'type': 'in', 'name': 'A'}, 'value')
        )
    )
    def update_warning_div(**kwargs):
        # need to follow optimization convention
        errs, block, severity = test_input(kwargs)
        print(errs)
        if len(errs) > 0:

            div_contents = [
                'The following parameters may be invalid:',
                html.Br(), html.Br()
            ]

            for e in errs:
                div_contents.append(e)
                div_contents.append(html.Br())

            return html.div(div_contents)

        else:
            return ""

    @app.callback(
        Output({'type': 'in', 'name': MATCH}, 'valid'),
        Output({'type': 'in', 'name': MATCH}, 'invalid'),
        Output({'type': 'in', 'name': MATCH}, 'value'),
        Input({'type': 'in', 'name': MATCH}, 'value'),
        Input({'type': 'in', 'name': MATCH}, 'id')
    )
    def check_validity(value, cid):
        err, block, severity = test_single_input(cid['name'], value)
        a = (len(err) == 0)
        return (a, block, value)  #

    return app.server

    def gaussian(height, center_x, center_y, width_x, width_y):
        return lambda x,y: height*np.exp(
                -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)
