#!/bin/python3

import contextlib
import numpy as np
import math
import torch

from torch.autograd import Variable
from model.naive_model import Geometry, MicroChannelCooler, naive_model
from model.limits import clamp_variables


def cancel_opt(inst):
    del inst
    with contextlib.suppress(Exception):
        torch.cuda.empty_cache()
    

def make_variables(in_vars,opt_names):
    if torch.cuda.is_available():
        dev = "cuda:0"
    else:
        dev = "cpu"

    device = torch.device(dev)
    
    old_var_dict = {}
    var_dict = {}
    for name in opt_names:
        old_var_dict[name] = torch.tensor(in_vars[name], dtype=torch.float32, requires_grad=True, device=device) 
        var_dict[name] = Variable(torch.tensor(in_vars[name], dtype=torch.float32, device=device), requires_grad=True,)
    return var_dict, old_var_dict

def output(var_dict, loss, err):
    # Step 5: Post-process results
    for var in var_dict.keys():
        var_dict[var] = var_dict[var].detach().cpu().numpy()

    # Step 6: Return results
    return [var_dict.values(), loss, err]

def sgd_model(parameter_choice, optimize_type, progress, learning_rate, num_iterations, **default):
    """
    Optimization using stochastic gradient-based optimization with PyTorch.

    Assuming we want to minimize the pressure drop (dP) while maintaining a certain level of heat flux (q). 

    Parameters:
        L (float): Channel length [m]
        W (float): Channel width [m]
        H (float): Channel depth [m]
        rho (float): Fluid density [kg/m^3]
        mu (float): Fluid dynamic viscosity [Pa*s]
        cp (float): Fluid specific heat capacity [J/(kg*K)]
        k (float): Fluid thermal conductivity [W/(m*K)]
        T_in (float): Fluid inlet temperature [K]
        T_w (float): Fluid wall temperature [K]
        Q (float): Fluid flow rate [uL/min]
        optimize_type (string): Pick a parameter to optimize: 'default', 'q', 'dP', 'T_out'
        parameter_choice (array): Given user parameters to optimize for. If parameters are picked, they will not be kept constant, allowing those parameters to be optimized.
        

    Returns:
        L (float): optimized length [m]
        W (float): optimized width [m]
        H (float): optimized depth [m]
    """
    
    # Step 1: Create PyTorch Variables for the input parameters
    opt_names = ["L", "W", "H"]
    var_dict, old_var_dict = make_variables(default,opt_names)

    # Step 2: Set the optimization hyperparameters
    # Step 3: Initialize the optimizer
    optimizer = torch.optim.SGD(var_dict.values(), lr=learning_rate)
    
    # Initialize the loss array (for plotting/debugging)
    loss = np.zeros(num_iterations)

    # Step 4: Optimization loop
    for i in range(num_iterations):
        # Clear the gradients from the previous iteration
        optimizer.zero_grad(set_to_none=True)           

        # Solve using Naive method
        default.update(var_dict)
        q_torch,dP_torch, T_out = naive_model(**default)

        # Compute the objective function
        if optimize_type == 'default':
            objective = dP_torch - q_torch
            # print(objective.item())
        elif optimize_type == 'q':
            objective = -q_torch     # Email Tejawsi about manufacturing constraints s.t. we'll have ranges to clamp on.
        elif optimize_type == 'dP':
            objective = dP_torch
        elif optimize_type == 'T_out':
            objective = (T_out - T_in) ** 2
        else:
            raise ValueError("Invalid optimize_type, must be 'q', 'dP', or 'T_out'")

        # Save the loss / objective value for debugging/plotting
        loss[i] = objective.item()
        if not math.isfinite(loss[i]):
            return output(var_dict, loss, "Objective / Loss has diverged.")

        # Compute the gradients
        objective.backward()

        # Update the parameters
        optimizer.step()

        # Clamp L
        clamp_variables(var_dict, old_var_dict, parameter_choice)

        # update progress bar
        if progress:
            progress(
                [
                    str(i),
                    str(num_iterations),
                ]
            )

    return output(var_dict, loss, None)


class SGD_MicroChannelCooler(MicroChannelCooler):

    def solve_sgd(self, parameter_choice, optimize_type='default', progress=None, learning_rate = 1e-5, num_iterations = 100):
        '''
        Returns the optimized length, width, and depth using the gradient descent method w/ PyTorc

        Parameters:
            parameter_choice (array): Given user parameters to optimize for. If parameters are picked, they will not be kept constant, allowing those parameters to be optimized.
            optimize_type (string): Pick a parameter to optimize: 'default', 'q', 'dP', 'T_out'

        Returns:
            L (float): optimized length [m]
            W (float): optimized width [m]
            H (float): optimized depth [m]
            loss (array): loss function over iterations
        '''
        params = {'L': self.geometry.L, 'W': self.geometry.W, 'H': self.geometry.H,
                  'rho': self.fluid.rho, 'mu': self.fluid.mu, 'cp': self.fluid.cp, 'k': self.fluid.k,
                  'T_in': self.T_in, 'T_w': self.T_w, 'Q': self.Q,}
        args,loss,err = sgd_model(parameter_choice, optimize_type, progress, learning_rate, num_iterations, **params)
        
        print(err)
        print(max(loss))

        return args
    

if __name__ == '__main__':
    
    import matplotlib.pyplot as plt
    from model.fluids import ethylene_glycol

    L = 0.1 # length of microchannel [m]
    W = 100e-6 # width of microchannel [m]
    H = 10 # depth of microchannel [m]

    T_in = 20 + 273 # inlet temperature [K]
    T_w = 100 + 273 # inlet temperature [K]

    Q = 100 # flow rate [uL/min]

    
    # q_list = []
    # dP_list = []
    # T_out_list = []

    geom = Geometry(L, W, H)
    cooler = SGD_MicroChannelCooler(geom, ethylene_glycol, T_in, T_w, 100)
    L_optimized, W_optimized, D_optimized = cooler.solve_sgd(parameter_choice = ['L','W'], optimize_type='default', progress=None)
    # q_list.append(q)
        # dP_list.append(dP)
        # T_out_list.append(T_out)
    print("Optimized L, W, H.")
    print("L: ", L_optimized, " W: ", W_optimized, " H: ", D_optimized)

    # q = np.array(q_list)
    # dP = np.array(dP_list)
    # T_out = T_out.detach().numpy()


    # Plot
    # fig, (ax1, ax2) = plt.subplots(1, 2)

    # fig.set_figwidth(10)
    # fig.set_figheight(6)
    # fig.tight_layout(pad=4)

    # # Plot naive model results
    # ax1.plot(D, dP * 0.000145038)
    # ax1.set_title("Naive Model")
    # ax1.set_xlabel("D ($\mu m$)")
    # ax1.set_ylabel("$\delta P$ (psi)")
    # ax1.set_xscale("log")

    # # Plot optimized results
    # ax2.plot(D, np.array(dP_list) * 0.000145038)
    # ax2.set_title("Optimized Model (SGD)")
    # ax2.set_xlabel("D ($\mu m$)")
    # ax2.set_ylabel("$\delta P$ (psi)")
    # ax2.set_xscale("log")

    # plt.show()
