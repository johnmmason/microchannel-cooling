from dash.exceptions import PreventUpdate
import torch

limits = {      
    'L': {
        'min': 0.02,
        'max': 0.1,
        'type': float,
    },
    'W': {
        'min': 1,
        'max': 1000,
        'type': float,
    },
    'H': {
        'min': 1,
        'max': 100,
        'type': float,
    },
    'T_in': {
        'min': 0,
        'max': 25,
        'type': float,
    },
    'T_w': {
        'min': 0,
        'max': 100,
        'type': float,
    },
    'Q': {
        'min': 1,
        'max': 1000,
        'type': float,
    },        
}

errMsg = {
    'L': 'Length',
    'W': 'Width',
    'H': 'Depth',
    'T_in': 'Inlet Temperature',
    'T_w': 'Wall Temperature',
    'Q': 'Flow Rate',
    'from': ' (start)',
    'to': ' (end)',
    'range': ' has invalid range.',
}

sev = ['[WARNING] ','[CRITICAL] '] # severity

def get_name(qvar):
    if '_' in qvar:
        ps = qvar.split('_')
        q = ps[-1]
        if q in ('from', 'to'):
            return "_".join(ps[:-1])
    return qvar

def swap_range(var_dict, qvar):
    ps = qvar.split('_')
    if ps[-1] == 'from':
        ps[-1] = 'to'
    return var_dict["_".join(ps)]

def get_err_msg(var, qvar):
    msg = errMsg[var]
    last = qvar.split('-')[-1]
    if last in ('from', 'to'):
        msg += errMsg[last]
    return msg

def test_single_input(qvar, val):
    errs = []
    severity = []
    try:
        var = get_name(qvar)
        if var in limits:
            try:
                val = limits[var]['type'](val)
                assert isinstance(val, limits[var]['type'])
            except TypeError as e:
                errs.append(f'{sev[1]}{get_err_msg(var, qvar)} is not a number')
                severity.append(1)
            else:                   
                if val < limits[var]['min'] or val > limits[var]['max'] or val is None:
                    errs.append(f'{sev[0]}{get_err_msg(var, qvar)} is not defined, or out of range')
                    severity.append(0)
    except Exception as e:
        raise PreventUpdate from e
    block = any(severity)
    return errs, block, severity


def test_input(var_dict):
    errs = []
    severity = []

    try:
        # check individual variables
        for qvar in var_dict.keys():
            try:
                var = get_name(qvar)
                if var in limits and qvar in var_dict:
                    try:
                        val = limits[var]['type'](var_dict[qvar])
                        assert isinstance(val, limits[var]['type'])
                    except TypeError as e:
                        errs.append(f'{sev[1]}{get_err_msg(var, qvar)} is not a number')
                        severity.append(1)
                    else:                   
                        if val < limits[var]['min'] or val > limits[var]['max'] or val is None:
                            errs.append(f'{sev[0]}{get_err_msg(var, qvar)} is not defined, or out of range')
                            severity.append(0)
            except Exception as e:
                raise PreventUpdate from e
        # check ranges
        for qvar in var_dict.keys():
            var = get_name(qvar)
            try:
                if (
                    var in limits
                    and qvar.endswith('from')
                    and var_dict[qvar] >= swap_range(var_dict, qvar)
                ):
                    errs.append(sev[0] + errMsg[var] + errMsg['range'])
                    severity.append(0)
            except Exception as e:
                raise PreventUpdate from e
    except Exception as e:
        raise PreventUpdate from e
    block = any(severity)
    return errs, block, severity


def clamp_variables(opt,old_opt,parameter_choice):
    for var in opt:
        if var in limits:
            if var in parameter_choice:
                opt[var] = torch.clamp(opt[var], min=limits[var]['min'], max=limits[var]['max'])
                opt[var] = opt[var].detach()
            else:
                opt[var] = old_opt[var]