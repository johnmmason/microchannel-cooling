from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import diskcache
from gui.dash_template import new_app_opt
from model.naive_model import Geometry
from model.fluids import fluids, fluidoptions
from dash.long_callback import DiskcacheLongCallbackManager
from model.sgd_model import SGD_MicroChannelCooler
import time

def make_naive_app_opt(server, prefix):

    cache = diskcache.Cache("./cache")
    long_manager = DiskcacheLongCallbackManager(cache)

    app = new_app_opt(server, prefix, long_manager, centered='center')
    app.title = "Naive Model"
    app.version = 0.1
    # don't use H2 - that is reserved for dropdowns in Flask right now
    app.layout = html.Div([
        html.H1("Microchannel Cooling, Naive Method Optimization", className='rh-align'),
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
                           {'label': 'Depth', 'value': 'D'},
                       ],
                       value=['D'], id ='par', className='input-box')]),
                    html.Br(),
                    # I think this is important for user to choose
                    html.Div(["Fluid:",
                        dbc.Select(fluidoptions, value = 'Water', id='fluid')],
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

    @app.long_callback(
        output=Output("paragraph_id", "children"),
        inputs=[
            Input('button_id', 'n_clicks'),
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



    def callback(set_progress, n_clicks, par, fluid):
        if n_clicks > 0:
            L = 0.1 # length of microchannel [m]
            W = 100e-6 # width of microchannel [m]
            D = 50 * 1e-6 # depth of microchannel [m]

            T_in = 20 + 273.15 # inlet temperature [K]
            T_w = 100 + 273.15 # inlet temperature [K]

            Q = 100 # flow rate [uL/min]
            
            try: 
                F = fluids[fluid]
            except Exception as e:
                F = fluids[0]
    
            geom = Geometry(L, W, D)
            cooler = SGD_MicroChannelCooler(geom, F, T_in, T_w, Q)
            L_optimized, W_optimized, D_optimized = cooler.solve_sgd(parameter_choice = par, optimize_type='default', progress=set_progress, num_iterations=5000)

            return [f"L:\t{L_optimized},\nW:\t{W_optimized},\nD:\t{D_optimized}"]
        else:
            return["Optimize Channel Parameters:"]

    return app.server

