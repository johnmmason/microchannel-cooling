import base64, io
import numpy as np
import pandas as pd
from scipy.interpolate import LinearNDInterpolator
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, ctx, MATCH, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from gui.dash_template import new_app
from model.naive_model import MicroChannelCooler, Geometry
from model.fluids import fluids, fluidoptions
from model.limits import test_input, test_single_input
from config import update_style
def make_naive_anly(server, prefix):

    app = new_app(server, prefix, centered='center')
    app.title = "Naive Model"
    app.version = 0.1
    # don't use H2 - that is reserved for dropdowns in Flask right now
    app.layout = html.Div([
        html.H1("Microchannel Cooling, Naive Analysis", className='rh-align'),
        html.Div([
            html.Div([
                html.Div(id='err'),
                html.Br(),
		        html.Div(["Fluid:",
                    dbc.Select(fluidoptions, placeholder="Water", value = 0, id={'type': 'in', 'name': 'fluid'})],
                   className='input-box'),
                html.Div(["Length (m):", dbc.Input(id={'type': 'in', 'name': 'L'}, value='0.01', type='number')], className='input-box'),
                html.Div(["Width (um):", dbc.Input(id={'type': 'in', 'name': 'W'}, value='100',  type='number')], className='input-box'),
                html.Div(["Depth (um):", dbc.Input(id={'type': 'in', 'name': 'H'}, value='10', type='number')], className='input-box'),
                html.Div(["Inlet Temperature (C):", dbc.Input(id={'type': 'in', 'name': 'T_in'}, value='20', type='number')], className='input-box'),
                html.Div(["Wall Temperature (C):",  dbc.Input(id={'type': 'in', 'name': 'T_w'}, value='100', type='number')], className='input-box'),
                html.Div(["Flow Rate (uL/min):",    dbc.Input(id={'type': 'in', 'name': 'Q'}, value='100', type='number')], className='input-box'),
                dcc.Upload(
                    id='upload-csv',
                    children=html.Div([
                        'Autodesk CFD nodal CSV / Starts processing on upload.',
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=False
                ),
            ], className='input'),
            html.Div(className='hspace'),
            html.Div([dcc.Graph(id='plot')], className='plot'),
        ], className='row'),
        html.Div(id='cancel_button_id', style={'display': 'none'}), # workaround for dash errors.
    ])

    @app.callback(
        Output(component_id='plot', component_property='figure'),
        State({'type': 'in', 'name': 'fluid'},'value'),
        State({'type': 'in', 'name': 'L'},'value'),
        State({'type': 'in', 'name': 'W'},'value'),
        State({'type': 'in', 'name': 'H'},'value'),
        State({'type': 'in', 'name': 'T_in'},'value'),
        State({'type': 'in', 'name': 'T_w'},'value'),
        State({'type': 'in', 'name': 'Q'}, 'value'),
        Input('upload-csv', 'contents'),
        prevent_initial_call=True
    )
    def update_output_div(fluid, L, W, H, temp_inlet, temp_wall, flow_rate, contents):

        try:
            L = float(L) # L of microchannel [m]
            W = float(W) * 1e-6 # W of microchannel [m]
            H = float(H) * 1e-6 # H of microchannel [m]
            try: 
                F = fluids[int(fluid)]
            except Exception as e:
                print(e)
                F = fluids[0]

            T_in = float(temp_inlet) + 273.15 # temperature of inlet [K]
            T_w = float(temp_wall) + 273.15 # temperature of wall [K]
            Q = float(flow_rate) # flow rate [uL/min]m]

            

        except:
            raise PreventUpdate

            
        geom = Geometry(L, W, H)
        cooler = MicroChannelCooler(geom, F, T_in, T_w, Q)
        x,temp = cooler.solve(make_fields=True)

        # CSV
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df = np.split(df, df[df.isnull().all(1)].index)[0] # split on NaN rows and take first
        df = df.sort_values(by=['X'])
        cW = df[df['Density'] < 2.3] #TODO: remove hard-coded Si density
        cW = cW.sort_values(by=['X'])
        cx = cW['X'] - min(cW['X'])
        cx *= 0.01 # convert to m
        cy = cW['Y']*0.01 # convert to m
        cz = cW['Z']*0.01 # convert to m
        cT = cW['Temp']
        vx = cW['Vx Vel']
        vy = cW['Vy Vel']
        vz = cW['Vz Vel']
        
        fig = make_subplots(rows=1, cols=2, column_widths=[.33, .66], specs=[[{"type": "xy"}, {"type": "volume"}, {"type": "volume"}]])
        update_style(fig)
        
        fig.add_trace(row=1, col=1, trace=go.Scatter(x=x, y=temp-273.15, line_color='red', name='Model'))
        fig.add_trace(row=1, col=1, trace=go.Scatter(x=cx, y=cT-273.15, line_color='blue', name='CFD'))
        fig.update_xaxes(title_text="Channel Length (m)", row=1, col=1)
        fig.update_yaxes(title_text="Outlet Temperature (C)", row=1, col=1)
        
        
        fit_data = np.array([cx,cy,cz]).T
        interp = LinearNDInterpolator(fit_data, cT)
        x_ = np.linspace(min(cx),max(cx), 100)
        y_ = np.linspace(min(cy),max(cy), 20)
        z_ = np.linspace(min(cz),max(cz), 20)

        x, y, z = np.meshgrid(x_, y_, z_, indexing='ij')
        cT2 = interp((x, y, z))
        
        fig.add_trace(row=1, col=2, trace=go.Volume(
                                                x=x,
                                                y=y,
                                                z=z,
                                                value=cT2,
                                                isomin=0,
                                                isomax=100,
                                                opacity=0.1, # needs to be small to see through all surfaces
                                                surface_count=17, # needs to be a large number for good volume rendering
                                                name='Temperature',
                                                ))
        
        fig.add_trace(row=1, col=2, trace=go.Cone(
                                            x=cx,
                                            y=cy,
                                            z=cz,
                                            u=vx,
                                            v=vy,
                                            w=vz,
                                            colorscale='Blues',
                                            sizemode="absolute",
                                            sizeref=40,
                                            name='Velocity',))
                                                        
        fig.update_layout(yaxis_range=[0,100])
        fig.update_layout(height=600, showlegend=False)
        
            
        return fig

    @app.callback(
        Output('err', 'children'),
        inputs = dict(
            fluid = Input({'type': 'in', 'name': 'fluid'},'value'),
            L = Input({'type': 'in', 'name': 'L'},'value'),
            W = Input({'type': 'in', 'name': 'W'},'value'),
            H = Input({'type': 'in', 'name': 'H'},'value'),
            T_in = Input({'type': 'in', 'name': 'T_in'},'value'),
            T_w = Input({'type': 'in', 'name': 'T_w'},'value'),
            Q = Input({'type': 'in', 'name': 'Q'}, 'value')
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
        err,block,severity = test_single_input(cid['name'], value)
        a = (len(err) == 0)
        return (a, block, value) #
    
    return app.server