import numpy as np
import matplotlib.pyplot as plt
import torch

from torch.autograd import Variable
from naive_model import Geometry, MicroChannelCooler
from fluids import Fluid, water

    
def sgd_model(L, W, D, rho, mu, cp, k, T_in, T_w, Q, optimize_type):
    """
    Optimization using stochastic gradient-based optimization with PyTorch.

    Assuming we want to minimize the pressure drop (dP) while maintaining a certain level of heat flux (q). 

    Parameters:
        L (float): Channel length [m]
        W (float): Channel width [m]
        D (float): Channel depth [m]
        rho (float): Fluid density [kg/m^3]
        mu (float): Fluid dynamic viscosity [Pa*s]
        cp (float): Fluid specific heat capacity [J/(kg*K)]
        k (float): Fluid thermal conductivity [W/(m*K)]
        T_in (float): Fluid inlet temperature [K]
        T_w (float): Fluid wall temperature [K]
        Q (float): Fluid flow rate [uL/min]
        optimize_type (string): Pick a parameter to optimize: 'q', 'dP', 'T_out'

    Returns:
        q (float): Heat flux [W/m^2]
        dP (float): Pressure drop [Pa]
        T_out (float): Outlet temperature [K]
    """

    # Step 1: Create PyTorch Variables for the input parameters
    L = Variable(torch.tensor(L, dtype=torch.float32), requires_grad=True)
    W = Variable(torch.tensor(W, dtype=torch.float32), requires_grad=True)
    D = Variable(torch.tensor(D, dtype=torch.float32), requires_grad=True)

    # Step 2: Set the optimization hyperparameters
    learning_rate = 1e-5
    num_iterations = 1000

    # Step 3: Initialize the optimizer
    optimizer = torch.optim.SGD([L, W, D], lr=learning_rate)

    # Step 4: Optimization loop
    for i in range(num_iterations):
        # Clear the gradients from the previous iteration
        optimizer.zero_grad()

        '''
        # Calculate the objective function
        geom = Geometry(L.item(), W.item(), D.tolist())
        cooler = MicroChannelCooler(geom, water, T_in, T_w, Q)
        q, dP, T_out = cooler.solve()
        
        # Convert the results to PyTorch tensors
        q_torch = torch.tensor(q, dtype=torch.float32)
        dP_torch = torch.tensor(dP, dtype=torch.float32)
        '''

        # Solve using Naive method
        A = W * D
        P = 2 * (W + D)
        Dh = 4 * A / P
        v = Q * 1.67e-11 / A
        Re = (rho * v * Dh) / mu
        Pr = cp * mu / k
        Nu = 0.023 * Re**(4/5) * Pr**(1/3)
        h = Nu * k / Dh
        q_torch = h * (T_w - T_in)
        f = 64 / Re
        dP_torch = (f * L * rho * (v**2)) / (2 * D)
        T_out = T_in + q_torch / (rho * Q * 1.67e-4 * cp)

        # Calculate objective
          # Default. Minimizing the pressure drop and maximizing the heat flux.
          # Heat flux q. Minimize the heat flux q. 
          # Pressure drop dP. Minimize pressure drop dP. 
          # Outlet temperature T_out. Minimize the temperature difference between the outlet and inlet temperatures, as to minimize the temperature rise in the fluid. Thus, the objective is defined as (T_out - T_in) ** 2 to penalize large temperature differences
        
        if optimize_type == 'default':
            objective = dP_torch - q_torch
        elif optimize_type == 'q':
            objective = q_torch     # Not sure if this objective is correct. 
        elif optimize_type == 'dP':
            objective = dP_torch
        elif optimize_type == 'T_out':
            objective = (T_out - T_in) ** 2
        else:
            raise ValueError("Invalid optimize_type, must be 'q', 'dP', or 'T_out'")


        # Compute the gradients
        objective.backward()

        # Update the parameters
        optimizer.step()

    # Step 5: Post-process results
    q = q_torch.detach().numpy()
    dP = dP_torch.detach().numpy()

    # Step 6: Return results
    return q, dP, T_out


class SGD_MicroChannelCooler(MicroChannelCooler):

    def solve_sgd(self, optimize_type='default'):
        '''
        Returns the heat flux, pressure drop, and output temperature using the gradient descent method w/ PyTorc

        Returns:
            q : the heat flux [W/m^2]
            dP : the pressure loss [Pa]
            T_out : the outlet temperature [K]
        '''

        q, dP, T_out = sgd_model(self.geometry.L, self.geometry.W, self.geometry.D,
                                   self.fluid.rho, self.fluid.mu, self.fluid.cp, self.fluid.k,
                                   self.T_in, self.T_w, self.Q, optimize_type)

        return q, dP, T_out
    

if __name__ == '__main__':

    L = 0.1 # length of microchannel [m]
    W = 100e-6 # width of microchannel [m]
    D = np.arange(10, 50, 1) * 1e-6 # depth of microchannel [m]

    T_in = 20 + 273 # inlet temperature [K]
    T_w = 100 + 273 # inlet temperature [K]

    Q = 100 # flow rate [uL/min]

    
    q_list = []
    dP_list = []
    T_out_list = []

    for D_scalar in D:
        geom = Geometry(L, W, D_scalar)
        cooler = SGD_MicroChannelCooler(geom, water, T_in, T_w, 100)
        q, dP, T_out = cooler.solve_sgd(optimize_type='dP')
        q_list.append(q)
        dP_list.append(dP)
        T_out_list.append(T_out)

    q = np.array(q_list)
    dP = np.array(dP_list)
    T_out = T_out.detach().numpy()

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2)

    fig.set_figwidth(10)
    fig.set_figheight(6)
    fig.tight_layout(pad=4)

    # Plot naive model results
    ax1.plot(D, dP * 0.000145038)
    ax1.set_title("Naive Model")
    ax1.set_xlabel("D ($\mu m$)")
    ax1.set_ylabel("$\delta P$ (psi)")
    ax1.set_xscale("log")

    # Plot optimized results
    ax2.plot(D, np.array(dP_list) * 0.000145038)
    ax2.set_title("Optimized Model (SGD)")
    ax2.set_xlabel("D ($\mu m$)")
    ax2.set_ylabel("$\delta P$ (psi)")
    ax2.set_xscale("log")

    plt.show()
