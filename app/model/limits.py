limits = {
    
        #     L (float): Channel length [m]
        # W (float): Channel width [m]
        # D (float): Channel depth [m]
        # rho (float): Fluid density [kg/m^3]
        # mu (float): Fluid dynamic viscosity [Pa*s]
        # cp (float): Fluid specific heat capacity [J/(kg*K)]
        # k (float): Fluid thermal conductivity [W/(m*K)]
        # T_in (float): Fluid inlet temperature [K]
        # T_w (float): Fluid wall temperature [K]
        # Q (float): Fluid flow rate [uL/min]
        
        
    'L': {
        min: 0,
        max: 0.1
    },
    'W': {
        min: 0,
        max: 1000
    },
    'D': {
        min: 0,
        max: 100
    },
    'T_in': {
        min: 0,
        max: 25
    },
    'T_w': {
        min: 0,
        max: 100
    },
    'Q': {
        min: 1,
        max: 1000
    },        
}

errMsg = {
    'L': 'Length',
    'W': 'Width',
    'D': 'Depth',
    'temp_inlet': 'Inlet Temperature',
    'temp_wall': 'Wall Temperature',
    'flow_rate': 'Flow Rate',
    'from': ' (start)',
    'to': ' (end)',
    'range': 'Invalid range',
}

sev = ['[WARNING] ','[CRITICAL] '] # severity

def test_input(var_dict):
    errs = []
    severity = []
    try:
        for var in var_dict:
            if var in limits:
                msg = None
                if var_dict[var] < limits[var]['min']:
                    msg = errMsg[var]
                elif var_dict[var] > limits[var]['max']:
                    msg = errMsg[var]
                if msg:
                    last = var.split('-')[-1]
                    if last in ('from', 'to'):
                        msg += errMsg[last]
                    errs.append(f'{sev[0]}{msg} is out of range')
                    severity.append(0)
                if var.endswith('from') and var_dict[var] >= var_dict[var.replace('from', 'to')]:
                    errs.append(sev[1] + errMsg[var] + errMsg['range'])
                    severity.append(1)
    except ValueError as e:
        raise PreventUpdate from e
    block = any(severity==1)
    return errs, block, severity

def clamp_variables(opt,parameter_choice):
    for var in opt.__dict__:
        if var in limits:
            if var in parameter_choice:
                opt.__dict__[var] = torch.clamp(opt.__dict__[var], min=limits[var]['min'], max=limits[var]['max'])
                opt.__dict__[var] = opt.__dict__[var].detach()
            else:
                opt.__dict__[var] = opt.__dict__[f'{var}_old']