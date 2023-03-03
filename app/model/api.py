import json
from flask import Blueprint, request
from flask_expects_json import expects_json
from model import schemes
from model.naive_model import Geometry, MicroChannelCooler
from model.fluids import water

model = Blueprint('model', __name__)

@model.route("/naive", methods=['POST'])
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
    