#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from model.fluids import Fluid, water

def naive_model(L, W, D, rho, mu, cp, k, T_in, T_w, Q):
    # Uses the Naive Model to calculate heat flux, pressure drop, and output temperature
    # for a microchannel cooling system

    A = W * D # cross-sectional area [m^2]
    P = 2 * (W + D) # wetted perimeter [m]
    Dh = 4 * A / P # hydraulic diameter [m]

    v = Q * 1.67e-11 / A # fluid velocity [m/s]

    Re = (rho * v * Dh) / mu # Reynolds number [ul]
    Pr = cp * mu / k # Prandtl number [ul]
    Nu = 0.023 * Re**(4/5) * Pr**(1/3) # Nusselt number[ul]

    h = Nu * k / Dh; # heat transfer coefficient [W/(m^2*K)]

    q = h * (T_w - T_in); # heat flux [W/m^2]

    f = 64/Re
    dP = ( f * L * rho * (v**2) ) / ( 2 * D ) # pressure loss [Pa]

    T_out = T_in + q / (rho * Q * 1.67e-4 * cp) # outlet temperature [K]

    return q, dP, T_out

class Geometry:
    def __init__(self, L, W, D):
        # Initialize Geometry
        #
        # L : channel length [m]
        # W : channel width [m]
        # D : channel width [m]
        
        self.L = L
        self.W = W
        self.D = D

class MicroChannelCooler:

    def __init__(self, geometry, fluid, T_in, T_w, Q):
        # Initialize MicroChannelCooler
        #
        # geometry : a Geometry
        # fluid : a Fluid
        # T_in : fluid inlet temperature [K]
        # T_w : fluid wall temperature [K]
        # Q : fluid flow rate [uL/min]
        
        self.geometry = geometry
        self.fluid = fluid
        self.T_in = T_in
        self.T_w = T_w
        self.Q = Q
        
    def solve(self):
        # Returns the heat flux, pressure drop, and output temperature using the naive method
        #
        # Returns
        # q : the heat flux [W/m^2]
        # dP : the pressure loss [Pa]
        # T_out : the outlet temperature [K]
        
        q, dP, T_out = naive_model(self.geometry.L, self.geometry.W, self.geometry.D,
                                   self.fluid.rho, self.fluid.mu, self.fluid.cp, self.fluid.k,
                                   self.T_in, self.T_w, self.Q)

        return q, dP, T_out

if __name__ == '__main__':

    L = 0.1 # length of microchannel [m]
    W = 100e-6 # width of microchannel [m]
    D = np.arange(10, 50, 1) * 1e-6 # depth of microchannel [m]

    T_in = 20 + 273.15 # inlet temperature [K]
    T_w = 100 + 273.15 # inlet temperature [K]

    Q = 100 # flow rate [uL/min]

    
    geom = Geometry(L, W, D)
    cooler = MicroChannelCooler(geom, water, T_in, T_w, 100)
    q, dP, T_out = cooler.solve()


    fig, (ax1, ax2, ax3)  = plt.subplots(1, 3)

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

    ax3.plot( D, T_out-273.15 )
    ax3.set_xlabel('D ($\mu m$)')
    ax3.set_ylabel('Output Coolant Temperature ($^\circ C$)')
    ax3.set_xscale('log')

    plt.show()
