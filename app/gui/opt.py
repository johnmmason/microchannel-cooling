import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from gui.dash_template import new_app, new_app_opt
from model.naive_model import MicroChannelCooler, Geometry
from model.fluids import water, ethylene_glycol, silicon_dioxide_nanofluid, mineral_oil
from dash.long_callback import DiskcacheLongCallbackManager
from config import update_style
def make_naive_app_opt(server, prefix):

    import diskcache
    cache = diskcache.Cache("./cache")
    long_callback_manager = DiskcacheLongCallbackManager(cache)

    app = new_app_opt(server, prefix, long_callback_manager, centered='center')
    app.title = "Naive Model"
    app.version = 0.1
    # don't use H2 - that is reserved for dropdowns in Flask right now
    app.layout = html.Div([
        html.H1("Microchannel Cooling, Naive Method Optimization", className='rh-align'),
        html.Div([
            html.Div([
                html.Div(["Choose a parameter to optimize:",
                    dcc.RadioItems([
                                 {'label': 'Length', 'value': 'length'},
                                 {'label': 'Width', 'value': 'width'},
                                 {'label': 'Depth', 'value': 'depth'},
                                 {'label': 'No Optimization', 'value': 'no'},
                                 ], value = 'no', id = 'opt')],
                   ),
		        html.Div(["Select a Fluid",
                    dcc.Dropdown(['Water',
                                  'Ethylene glycol',
                                  'Silicon dioxide nanofluid',
                                  'Mineral oil'
                                  ], value = 'Water', id='fluid')],
                   ),
                html.Div([
                html.P(id="paragraph_id", children=["Button not clicked"]),
                html.Progress(id="progress_bar"),
                ]),
                html.Button(id="button_id", children="Run Job!"),
                html.Button(id="cancel_button_id", children="Cancel Running Job!"),
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
        total = 10
        for i in range(total):
            time.sleep(0.5)
            set_progress((str(i + 1), str(total)))
        return [f"Clicked {n_clicks} times"]

