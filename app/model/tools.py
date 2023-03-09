#!/bin/python3

import json, copy
import numpy as np

def convert_numpy_to_list(d):

    for param, value in d.items():

        if type(value) is np.ndarray:
            d[param] = value.tolist()

def preprocess_input(raw):

    d = copy.deepcopy(raw)
    
    for param, value in d.items():
        
        if type(value) in [int, float, str]:
            pass # do nothing

        elif type(value) in [dict]:
            d[param] = to_model_input(value)

        else:
            raise TypeError('unknown input')

    return d

def to_model_input(j):

    if type(j) in [int, float] : return j

    elif type(j) is dict:

        if j['type'] == 'arange':

            start = j['start']
            stop = j['stop']

            try:
                step = j['step']
            except KeyError:
                step = None

            if step is not None:
                return np.arange(start, stop, step)
            else:
                return np.arange(start, stop)

        elif j['type'] == 'linspace':

            start = j['start']
            stop = j['stop']

            try:
                num = j['num']
            except KeyError:
                num = None

            if num is not None:
                return np.linspace(start, stop, num=num)
            else:
                return np.linspace(start, stop)

    else : raise TypeError('unsupported type for model input')

if __name__ == '__main__':

    j = {
        'type':'arange',
        'start':10,
        'stop':100,
        'step':10
    }

    print(
        to_model_input(j)
        )
