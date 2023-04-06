#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from model.fluids import Fluid, water

def naive_model(L, W, H, rho, mu, cp, k, T_in, T_w, Q, N_ELE=1000):
    # Calculate the heat transfer in a rectangular microchannel with the specified
    # properties using a 1-dimensional enthalpy heat transfer model
    #
    # L : channel length [m]
    # W : channel width [m]
    # H : channel height/depth [m]
    # rho : density [kg/m^3]
    # mu : viscosity [Pa*s]
    # cp : heat capacity [J/kg*K]
    # k : thermal conductivity [W/m*K]
    # T_in : fluid temperature at inlet [K]
    # T_w : wall temperature [K]
    # Q : fluid flow rate [uL/min]
    #
    # Returns
    # q : the heat flux [W/cm2]
    # dP : the backpressure [Pascal]
    # T_out : the fluid temperature at the outlet [K]

    A = W * H # cross-sectional area [m^2]
    P = 2 * (W + H) # perimeter [m]
    D = 4 * A / P # hydraulic diameter [m]

    Q_SI = Q * 1e-9 / 60 # flow rate [m^3/s]

    v = Q_SI / A # fluid velocity [m/s]

    Re = rho * v * D / mu # Reynolds number
    Pr = cp * mu / k # Prandtl number
    Nu = 0.023 * Re**0.8 * Pr**0.4 # Nusselt number

    h = Nu * k / D # heat transfer coefficient

    f = 64/Re
    dP = ( f * L * rho * (v**2) ) / ( 2 * H ) # pressure loss [Pa]

    dL = L/N_ELE
    
    T = np.empty(N_ELE); T[0] = T_in
    E = 0

    for i in range(1, N_ELE):

        T_in_ = T[i-1] # element inlet temperature [K]

        dE = 4 * h * W * dL * (T_w - T_in_) # heat transfer [W]
        T_out = (dE / (rho * Q_SI * cp)) + T_in_ # element outlet temperature [K]

        T[i] = T_out
        E += dE

    q = E / ( 4 * W * L * 10000 )
    
    return q, dP, T[N_ELE-1]

class Geometry:
    def __init__(self, L, W, H):
        # Initialize Geometry
        #
        # L : channel length [m]
        # W : channel width [m]
        # H : channel width [m]
        
        self.L = L
        self.W = W
        self.H = H

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
        # Returns the heat flux, pressure drop, and output temperature
        # using the naive method
        #
        # Returns
        # q : the heat transfer [W/cm^3]
        # dP : the pressure loss [Pa]
        # T_out : the outlet temperature [K]
        
        q, dP, T_out = naive_model(self.geometry.L,
                                   self.geometry.W,
                                   self.geometry.H,
                                   self.fluid.rho,
                                   self.fluid.mu,
                                   self.fluid.cp,
                                   self.fluid.k,
                                   self.T_in,
                                   self.T_w,
                                   self.Q)

        return q, dP, T_out

def main():

    L = 0.1 # length of microchannel [m]
    W = 100e-6 # width of microchannel [m]
    H = 100e-6 # depth of microchannel [m]

    T_in = 20 + 273.15 # inlet temperature [K]
    T_w = 100 + 273.15 # inlet temperature [K]

    Q = 100 # flow rate [uL/min]

    geom = Geometry(L, W, H)
    cooler = MicroChannelCooler(geom, water, T_in, T_w, 100)
    E, dP, T_out = cooler.solve()

    print('Outlet temperature: {:.4f} C'.format(T_out - 273.15))
    print('Heat Flux: {:.4f} W/cm2'.format(E))
    print('Backpressure: {:.4f} PSI'.format(dP * 0.000145038))

if __name__ == '__main__':

    main()
