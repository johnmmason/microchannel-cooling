from time import sleep
import multiprocessing as mp
import ctypes
from flask import Blueprint, request as rq, render_template, redirect
import requests as rqs
import json as js
from config import base

gui = Blueprint('gui', __name__)
man = mp.Manager()

data = None # global variables to store data (a bit hacky, but this way we should have a loading screen)
state = [man.Value('i',0), man.Value('i',0), man.Value('i', 0), man.dict({'out':"Not Computed Yet"})] # iteration, total-iterations, status, result
states = ['Idle', 'Running', 'Done']
template_kwargs = {'template':"main", 'proxy':''}

# https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask
@gui.route('/naive', methods=['GET','POST'])
def naive() -> str:    
    global data, state

    if rq.method == 'POST' and state[0].value == 0:
        data = js.loads(rq.form['inpt'])
        mp.Process(target=method, args=['/model/naive', data, *state]).start()
        return render_template("blank.jinja2", display="Loading ...", **template_kwargs)

    elif data is None:
        return render_template("form.jinja2", title="Naive Method Input", **template_kwargs)
    
    else: 
        output = f"<b> Status: {states[state[2].value]} </b> <br> {'Iteration' if state[2].value != 2 else 'Result'} : {f'{state[0].value}/{state[1].value}' if state[2].value != 2 else state[3]['out']}"
        return render_template("blank.jinja2", display=output, **template_kwargs)


def method(*args):
    cstate = args[2:]
    nit = 10
    cstate[1].value = nit
    cstate[2].value = 1
    # fake iteration to simulate a long running job
    for iteration in range(nit):
        cstate[0].value = iteration
        sleep(0.5)

    result = rqs.post(f'{base}{args[0]}', json=args[1])

    cstate[2].value = 2
    cstate[3]['out'] = result.text

@gui.route('/<method>/clear', methods=['GET','POST'])
def clear(method) -> str:
    global data, state
    data = None
    state[0].value = 0
    state[1].value = 0
    state[2].value = 0
    state[3]['out'] = "Not Computed Yet"
    return redirect(f'/{method}')


