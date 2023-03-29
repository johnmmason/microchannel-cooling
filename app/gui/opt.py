import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import diskcache
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from gui.dash_template import new_app, new_app_opt
from model.naive_model import MicroChannelCooler, Geometry
from model.fluids import water, ethylene_glycol, silicon_dioxide_nanofluid, mineral_oil
from dash.long_callback import DiskcacheLongCallbackManager
from config import update_style
from model.sgd_model import sgd_model
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

                # Shruthi make checkboxes instead of radio buttons
                html.Div(["Choose a parameter to optimize:",
                    dcc.RadioItems([
                                 {'label': 'Length', 'value': 'length'},
                                 {'label': 'Width', 'value': 'width'},
                                 {'label': 'Depth', 'value': 'depth'},
                                 {'label': 'No Optimization', 'value': 'no'},
                                 ], value = 'no', id = 'opt')],
                   ),
                # I think this is important for user to choose
		        html.Div(["Select a Fluid",
                    dcc.Dropdown(['Water',
                                  'Ethylene glycol',
                                  'Silicon dioxide nanofluid',
                                  'Mineral oil'
                                  ], value = 'Water', id='fluid')],
                   ),
                # Cassandre make textboxes for initial input and then maximum iterations/ tolerance for 
                html.Div([
                html.P(id="paragraph_id", children=["Run Optimization"]),
                html.Progress(id="progress_bar"),
                ]),
                html.Button(id="button_id", children="Run", n_clicks=0),
                html.Button(id="cancel_button_id", children="Cancel Running Job"),
        ])

        ], className='row'),		
    ])

    @app.long_callback(
        output=Output("paragraph_id", "children"),
        inputs=Input("button_id", "n_clicks"),
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
    )

    def callback(set_progress, n_clicks):
        if n_clicks > 0:
            L = 0.1 # length of microchannel [m]
            W = 100e-6 # width of microchannel [m]
            D = np.arange(10, 50, 1) * 1e-6 # depth of microchannel [m]

            T_in = 20 + 273 # inlet temperature [K]
            T_w = 100 + 273 # inlet temperature [K]

            Q = 100 # flow rate [uL/min]

    
            # q_list = []
            # dP_list = []
            # T_out_list = []
            i = 1
            total = len(D)
            for D_scalar in D:
                geom = Geometry(L, W, D_scalar)
                i+1
                cooler = SGD_MicroChannelCooler(geom, ethylene_glycol, T_in, T_w, 100)
                L_optimized, W_optimized, D_optimized = cooler.solve_sgd(parameter_choice = [], optimize_type='default')
                # q_list.append(q)
                # dP_list.append(dP)
                # T_out_list.append(T_out)    
                set_progress((str(i + 1), str(total)))
            return [f"L: {L_optimized}, W: {W_optimized}, D: {D_optimized}"]
        else:
            return["Optimize"]

    return app.server

    return app.server