import json, copy, io
import numpy as np
from flask import Blueprint, request
from flask_expects_json import expects_json
from model import schemes
from model.naive_model import Geometry, MicroChannelCooler
from model.fluids import water
from model.tools import preprocess_input, convert_numpy_to_list

model = Blueprint('model', __name__)

@model.route("/naive", methods=['POST'])
@expects_json(schemes.naive)
def naive():

    global plot
    
    raw_data = request.get_json()
    data = preprocess_input(raw_data)
    
    geom = Geometry( data['L'], data['W'], data['D'] )
    cooler = MicroChannelCooler(geom, water, data['T_in'], data['T_w'], data['Q'])

    q, dP, T_out = cooler.solve()

    out = {
        'input': raw_data,
        'q' : q * 1e-4, # return q in W/cm^2
        'dP' : dP * 0.000145038, # return dP in PSI
        'T_out' : T_out - 273 # return T_out in C
    }

    convert_numpy_to_list(out)
    
    return json.dumps(out, indent=2)
