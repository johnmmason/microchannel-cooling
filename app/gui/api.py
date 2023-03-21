import multiprocessing as mp
from flask import Blueprint, request as rq, render_template, redirect, current_app
from flask import Response
import requests as rqs
import random
import io
import json as js
from config import base
import gui.input as input
##################

gui = Blueprint('gui', __name__)
man = mp.Manager()

##################
data = None # global variables to store data (a bit hacky, but this way we should have a loading screen)
state = [man.Value('i',0), man.Value('i',0), man.Value('i', 0), man.dict({'out':"Not Computed Yet"})] # iteration, total-iterations, status, result
states = ['Idle', 'Running', 'Done']
##################
## refresh rates
rf = 1
inf = 1e6
refresh_period = 1
##################
template_kwargs = {'template':"main", 'proxy':'', 'base':"layout.jinja2"}
##################
# https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask

# still working on this redirect for image
@gui.route("/redirect/<path:target>")
def redirect(target):
    return input.Form([],action=target).render()

@gui.route('/flask/<method>', methods=['GET','POST'])
def render(method) -> str:    
    global data, state
    form = input.Form(
            [
                input.textarea('inpt',title="Naive Method Input"),
            ],
            target="_blank",
            refresh_period = refresh_period,
            **template_kwargs)

    if rq.method == 'POST' and state[0].value == 0:
        try:
            data = js.loads(rq.form['inpt'])
            mp.Process(target=run, args=[f'/model/{method}', data, *state]).start()
            return render_template("blank.jinja2", **template_kwargs, refresh_period = refresh_period)
        except Exception as e:
            return form.render(error=f"Invalid JSON input: \n\t\t{e}")

    elif data is None:
        return form.render()
    
    else: 
        return render_template("blank.jinja2", **template_kwargs, refresh_period = refresh_period)

@gui.context_processor
def inject_display():
    global data, state, refresh_period
    centered = 'row center wrap-x'
    if data is None and state[0].value == 0:
        refresh_period = rf
        display="Loading ..."
    elif state[2].value == 2:
        refresh_period = inf
        display = f"<b> Status: {states[state[2].value]} </b> <br> Result : {state[3]['out']}"
        centered = 'row wrap-x'
    else:
        display = f"<b> Status: {states[state[2].value]} </b> <br> Iteration : {state[0].value}/{state[1].value}"
    return {'display': display,'centered': centered}


from time import sleep
def run(*args):
    cstate = args[2:]
    nit = 10
    cstate[1].value = nit
    cstate[2].value = 1
    # fake iteration to simulate a long running job
    for iteration in range(nit):
        cstate[0].value = iteration
        sleep(0.1)

    result = rqs.post(f'{base}{args[0]}', json=args[1])

    cstate[2].value = 2
    cstate[3]['out'] = result.text

@gui.route('/flask/<method>/clear', methods=['GET','POST'])
def clear(method) -> str:
    global data, state
    data = None
    state[0].value = 0
    state[1].value = 0
    state[2].value = 0
    state[3]['out'] = "Not Computed Yet"
    return redirect(f'/{method}')
	
 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
 
 
@gui.route('/testplot')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig

