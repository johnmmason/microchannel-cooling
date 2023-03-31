import json
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, ctx, MATCH, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from gui.dash_template import new_app
from model.naive_model import MicroChannelCooler, Geometry
from model.fluids import water, ethylene_glycol, silicon_dioxide_nanofluid, mineral_oil
from model.limits import test_input
from config import update_style
def make_naive_app(server, prefix):

    app = new_app(server, prefix, centered='center')
    app.title = "Naive Model"
    app.version = 0.1
    # don't use H2 - that is reserved for dropdowns in Flask right now
    app.layout = html.Div([
        html.H1("Microchannel Cooling, Naive Method", className='rh-align'),
        html.Div([
            html.Div([
                #html.Div(["Choose a parameter to optimize:",
                #    dcc.RadioItems([
                #                 {'label': 'Length', 'value': 'L'},
                #                 {'label': 'Width', 'value': 'W'},
                #                 {'label': 'Depth', 'value': 'depth'},
                #                 {'label': 'No Optimization', 'value': 'no'},
                #                 ], value = 'no', id = 'opt')],
                #   ),
                html.Div(id='err'),
                html.Br(),
		        html.Div(["Fluid:",
                    dbc.Select(['Water',
                                  'Ethylene Glycol',
                                  'Silicon Dioxide Nanofluid',
                                  'Mineral Oil'
                                  ], value = 'Water', id={'type': 'in', 'name': 'fluid'})],
                   className='input-box'),
                html.Div(["Length (m):", dbc.Input(id={'type': 'in', 'name': 'L'}, value='0.1', type='number')], className='input-box'),
                html.Div(["Width (um):", dbc.Input(id={'type': 'in', 'name': 'W'}, value='100',  type='number')], className='input-box'),
                html.Div(["Depth (um) (start):", dbc.Input(id={'type': 'in', 'name': 'D_from'}, value='10', type='number')], className='input-box'),
                html.Div(["Depth (um) (end):",   dbc.Input(id={'type': 'in', 'name': 'D_to'}, value='50', type='number')], className='input-box'),
                html.Div(["Inlet Temperature (C):", dbc.Input(id={'type': 'in', 'name': 'T_in'}, value='20', type='number')], className='input-box'),
                html.Div(["Wall Temperature (C):",  dbc.Input(id={'type': 'in', 'name': 'T_w'}, value='100', type='number')], className='input-box'),
                html.Div(["Flow Rate (uL/min):",    dbc.Input(id={'type': 'in', 'name': 'Q'}, value='100', type='number')], className='input-box'),
            ], className='input'),
            html.Div(className='hspace'),
            html.Div([dcc.Graph(id='plot')], className='plot'),
        ], className='row'),
        html.Div(id='cancel_button_id', style={'display': 'none'}), # workaround for dash errors.
    ])

    @app.callback(
        Output(component_id='plot', component_property='figure'),
        Input({'type': 'in', 'name': 'fluid'},'value'),
        Input({'type': 'in', 'name': 'L'},'value'),
        Input({'type': 'in', 'name': 'W'},'value'),
        Input({'type': 'in', 'name': 'D_from'},'value'),
        Input({'type': 'in', 'name': 'D_to'},'value'),
        Input({'type': 'in', 'name': 'T_in'},'value'),
        Input({'type': 'in', 'name': 'T_w'},'value'),
        Input({'type': 'in', 'name': 'Q'}, 'value')
    )
    def update_output_div(fluid, L, W, depth_from, depth_to, temp_inlet, temp_wall, flow_rate):

        try:
            L = float(L) # L of microchannel [m]
            W = float(W) * 1e-6 # W of microchannel [m]

            if fluid == 'Water':
                F = water
            elif fluid == 'Ethylene glycol':
                F = ethylene_glycol
            elif fluid == 'Silicon dioxide nanofluid':
                F = silicon_dioxide_nanofluid
            elif fluid == 'Mineral oil':
                F = mineral_oil
            else:
                F = water
            
            T_in = float(temp_inlet) + 273 # temperature of inlet [K]
            T_w = float(temp_wall) + 273 # temperature of wall [K]
            Q = float(flow_rate) # flow rate [uL/min]m]

            D_low = float(depth_from)
            D_high = float(depth_to)

            assert D_low < D_high
            D = np.arange( D_low, D_high, 1 ) * 1e-6 #depth of microchannel [m]
        except:
            raise PreventUpdate

        geom = Geometry(L, W, D)
        cooler = MicroChannelCooler(geom, F, T_in, T_w, Q)
        q, dP, T_out = cooler.solve()

        fig = make_subplots(rows=1, cols=2, column_widths=[.5, .5])

        fig.add_trace(row=1, col=1, trace=go.Scatter(x=D, y=q*1e-4))
        fig.add_trace(row=1, col=2, trace=go.Scatter(x=D, y=dP*0.000145038))

        fig.update_xaxes(title_text="Channel Depth (m)", row=1, col=1)
        fig.update_xaxes(title_text="Channel Depth (m)", row=1, col=2)
        fig.update_yaxes(title_text="Heat Flux (W/cm2)", row=1, col=1)
        fig.update_yaxes(title_text="Backpressure (psi)", row=1, col=2)

        fig.update_layout(height=600, showlegend=False)
        update_style(fig)
            
        return fig

    @app.callback(
        Output('err', 'children'),
        Input({'type': 'in', 'name': 'fluid'},'value'),
        Input({'type': 'in', 'name': 'L'},'value'),
        Input({'type': 'in', 'name': 'W'},'value'),
        Input({'type': 'in', 'name': 'D_from'},'value'),
        Input({'type': 'in', 'name': 'D_to'},'value'),
        Input({'type': 'in', 'name': 'T_in'},'value'),
        Input({'type': 'in', 'name': 'T_w'},'value'),
        Input({'type': 'in', 'name': 'Q'}, 'value')
    )
    def update_warning_div(fluid, L, W, D_from, D_to, T_in, T_w, Q):
        # need to follow optimization convention
        errs, block, severity = test_input(locals())
        print(errs)
        if len(errs) > 0:

            div_contents = [
                'The following parameters may be invalid:',
                html.Br(), html.Br()
                ]

            for e in errs:
                div_contents.append(e)
                div_contents.append(html.Br())
            
            return html.Div(div_contents)
                            
        else : return ""
        
    @app.callback(
        Output({'type': 'in', 'name': MATCH},'valid'),
        Output({'type': 'in', 'name': MATCH}, 'invalid'),
        Output({'type': 'in', 'name': MATCH}, 'value'),
        Input( {'type': 'in', 'name': MATCH},'value'),
        Input( {'type': 'in', 'name': MATCH},'id')
    )
    def check_validity(value, cid):
        err,block,severity = test_input({cid['name']: value})
        a = (len(err) == 0)
        return (a, block, value) #
    
    return app.server
