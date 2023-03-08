import json, copy, io
import numpy as np
from flask import Blueprint, Response, request
from flask_expects_json import expects_json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
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
    
    if data['output'] == 'plot':

        D = data['D']
        
        fig, (ax1, ax2)  = plt.subplots(1, 2)

        fig.set_figwidth(10)
        fig.set_figheight(6)
        fig.tight_layout(pad=4)
        
        ax1.plot( D, q * 10**(-4) )
        ax1.set_xlabel('D ($\mu m$)')
        ax1.set_ylabel('Heat Flux ($W/cm^2$)')
        ax1.set_xscale('log')
    
        ax2.plot( D, dP * 0.000145038 )
        ax2.set_xlabel('D ($\mu m$)')
        ax2.set_ylabel('$\delta P$ (psi)')
        ax2.set_xscale('log')

        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    else:
        return json.dumps(out, indent=2)
