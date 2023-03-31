limits = {       
    'L': {
        'min': 0,
        'max': 0.1,
        'type': float,
    },
    'W': {
        'min': 0,
        'max': 1000,
        'type': float,
    },
    'D': {
        'min': 0,
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
    'D': 'Depth',
    'T_in': 'Inlet Temperature',
    'T_w': 'Wall Temperature',
    'Q': 'Flow Rate',
    'from': ' (start)',
    'to': ' (end)',
    'range': 'Invalid range',
}

sev = ['[WARNING] ','[CRITICAL] '] # severity

def get_name(qvar):
    return qvar.split('-')[0] if '-' in qvar else qvar

def get_err_msg(var, qvar):
    msg = errMsg[var]
    last = qvar.split('-')[-1]
    if last in ('from', 'to'):
        msg += errMsg[last]
    return msg

def test_input(var_dict):
    errs = []
    severity = []
    
    try:
        # check individual variables
        for qvar in var_dict.keys():
            var = get_name(qvar)
            if var in limits:
                msg = None
                try:
                    val = limits[var]['type'](var_dict[qvar])
                except TypeError as e:
                    errs.append(f'{sev[1]}{get_err_msg(var, qvar)} is not a number')
                    severity.append(1)
                else:                   
                    if val < limits[var]['min'] or val > limits[var]['max'] or val is None:
                        errs.append(f'{sev[0]}{get_err_msg(var, qvar)} is not defined, or out of range')
                        severity.append(0)
        # check ranges
        for qvar in var_dict.keys():
            var = get_name(qvar)
            if (
                var in limits
                and qvar.endswith('from')
                and get_value(var, qvar)
                <= get_value(var, qvar.replace('from', 'to'))
            ):
                errs.append(sev[0] + errMsg[var] + errMsg['range'])
                severity.append(0)
                
    except ValueError as e:
        raise PreventUpdate from e
    block = any(severity)
    return errs, block, severity

def clamp_variables(opt,parameter_choice):
    for var in opt.__dict__:
        if var in limits:
            if var in parameter_choice:
                opt.__dict__[var] = torch.clamp(opt.__dict__[var], min=limits[var]['min'], max=limits[var]['max'])
                opt.__dict__[var] = opt.__dict__[var].detach()
            else:
                opt.__dict__[var] = opt.__dict__[f'{var}_old']