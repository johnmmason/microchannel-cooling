import uuid
from dash import dcc, html, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import diskcache
from gui.dash_template import new_app
from model.naive_model import Geometry
from model.fluids import fluids, fluidoptions
from dash.long_callback import DiskcacheLongCallbackManager
from model.sgd_model import SGD_MicroChannelCooler, cancel_opt
from model.limits import microscale, kelvin, limits
import time

def make_naive_app_opt(server, prefix):
    
    session_id = str(uuid.uuid4())

    cache = diskcache.Cache("./cache")
    long_manager = DiskcacheLongCallbackManager(cache)

    app = new_app(server, prefix, long_manager, centered='center')
    app.title = "Single Channel Enthalpy Transfer"
    app.version = 0.1
    # don't use H2 - that is reserved for dropdowns in Flask right now
    app.layout = html.Div([
        html.H1(f"{app.title} Optimization", className='rh-align'),
        html.Div([
            html.Div([

                # checkboxes
                html.Div([
                    html.H4("Choose Parameters to Optimize:"),
                    html.Br(),
                    dcc.Checklist(
                       options=[
                           {'label': 'Length', 'value': 'L'},
                           {'label': 'Width', 'value': 'W'},
                           {'label': 'Depth', 'value': 'H'},
                       ],
                       value=['H'], id ='par', className='input-box')]),
                    html.Br(),
                    # I think this is important for user to choose
                    html.Div(["Fluid:",
                        dbc.Select(fluidoptions, placeholder="Water", value = 0, id='fluid')],
                    className='input-box'),
                    # Cassandre needs to make textboxes for initial input and then maximum iterations/ tolerance for 
                    html.Br(),
                    html.Div([
                        html.P(id="paragraph_id", children=[
                            html.H4("Run Optimization"),
                            ]),
                        html.Progress(id="progress_bar"),
                    ]),
                    html.Br(),
                    html.Button(id="button_id", children="Run", n_clicks=0),
                    html.Button(id="cancel_button_id", children="Cancel Running Job"),
                ])

            ], className='input'),		
        ])
    
    def _session(session_id, fluid):
        @cache.memoize()
        def make_(session_id):
            
            # TODO make this automatic using structure in limits dict.
            # TODO add user override for initial values
            L = limits['L']['init'] # length of microchannel [m]
            W = limits['W']['init'] * microscale # width of microchannel [m]
            H = limits['H']['init'] * microscale # depth of microchannel [m]

            T_in = limits['T_in']['init'] + kelvin # inlet temperature [K]
            T_w = limits['T_w']['init'] + kelvin # inlet temperature [K]

            Q = limits['Q']['init'] # flow rate [uL/min]
            
            try: 
                F = fluids[fluid]
            except Exception as e:
                F = fluids[0]

            geom = Geometry(L, W, H)
            cooler = SGD_MicroChannelCooler(T_in, T_w, Q, geom, F)
            return cooler
        
        return make_(session_id)
  
    @app.long_callback(
        output=Output("paragraph_id", "children"),
        inputs=[
            Input('button_id', 'n_clicks'),
            Input('cancel_button_id', 'n_clicks'),
            State('par','value'),
            State('fluid','value'),
        ],
        running=[
            (Output("button_id", "disabled"), True, False),
            (Output("cancel_button_id", "disabled"), False, True),
            (
                Output("paragraph_id", "style"),
                {"visibility": "hidden"},
                {"visibility": "visible"},
            ),
            (
                Output("progress_bar", "style"),
                {"visibility": "visible"},
                {"visibility": "hidden"},
            ),
        ],
        cancel=[Input("cancel_button_id", "n_clicks")],
        progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
        prevent_initial_call=True,
    )



    def callback(set_progress, n_clicks, cancel, par, fluid): # don't remove the 'cancel' argument
        set_progress((0, 100))
        trigger = ctx.triggered[0]
        print(trigger)
        if trigger["prop_id"]=="cancel_button_id.n_clicks":
            print("canceling")
            cooler = _session(session_id, fluid) # get the session
            cancel_opt(cooler)
            return ["Optimization Canceled"]
        elif n_clicks > 0:
            cooler = _session(session_id, fluid) # make a new session
            L_optimized, W_optimized, H_optimized = cooler.solve_sgd(parameter_choice = par, optimize_type='default', progress=set_progress)
            return [f"Length:\t{L_optimized},\nWidth:\t{W_optimized},\nDepth:\t{H_optimized}"]
        else:
            return["Optimize Channel Parameters:"]

    return app.server

