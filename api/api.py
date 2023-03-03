#!/bin/python3

import json
from flask import Flask, request, send_from_directory
from flask_expects_json import expects_json
import schemes
from model.naive_model import Geometry, MicroChannelCooler
from model.fluids import water

app = Flask(__name__)

@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('gui/static/', path)

# routes follow

@app.route("/")
def hello_world():
    return "<center><h1>Hello, World!</h1></center>"

@app.route("/naive", methods=['POST'])
@expects_json(schemes.naive)
def naive():

    data = request.get_json()

    geom = Geometry(data['L'], data['W'], data['D'])
    cooler = MicroChannelCooler(geom, water, data['T_in'], data['T_w'], data['Q'])

    q, dP, T_out = cooler.solve()
    
    return json.dumps({
        'input': data,
        'q' : q * 1e-4, # return q in W/cm^2
        'dP' : dP * 0.000145038, # return dP in PSI
        'T_out' : T_out - 273 # return T_out in C
        }, indent=2)
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
