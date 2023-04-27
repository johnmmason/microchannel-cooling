#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from model.fluids import Fluid, water

def naive_model(T_in, T_w, Q,
                L, W, H,
                rho, mu, cp, k, T_boiling_point,
                latent_heat_of_vaporization,              
                make_fields=False, N_ELE=1000, **kwargs):
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
    
    # References:
    # https://en.wikipedia.org/wiki/Nusselt_number
    # https://www.sciencedirect.com/science/article/pii/S0301932221000987
    
    
    # Nu_DB = 0.023 * Re**0.8 * Pr**0.4 # Nusselt number, uncorrected, original Dittus-Boelter (1930)
    # can add Sieder-Tate (1956) correction if we have viscosity as a function of temperature
    # Nu = 2 + 0.6 * Re**0.5 * Pr**(1/3) # Nusselt number, uncorrected (Ranz-Marshall, 1952)
    Nu_uncor = 2 + 0.552 * Re**0.5 * Pr**(1/3) # Nusselt number, uncorrected (Zhuifu, 2013)
    
    
    BTp = cp * (T_w - T_boiling_point) / latent_heat_of_vaporization # Spalding number
    fT = (1 + BTp)**(-2/3) # Zhuifu model (2013)
    Nu = Nu_uncor*fT # Nusselt number, correction for Zhuifu model (2013)

    f = 64/Re
    dP = ( f * L * rho * (v**2) ) / ( 2 * H ) # pressure loss [Pa]

    dL = L/N_ELE
    
    T = np.empty(N_ELE)
    T[0] = T_in
    E = 0

    for i in range(1, N_ELE):

        T_in_ = T[i-1] # element inlet temperature [K]
                
        h = Nu * k / D # heat transfer coefficient
        dE = 2 * h * (W+H)* dL * (T_w - T_in_) # heat transfer [W]
        T_out = (dE / (rho * Q_SI * cp)) + T_in_ # element outlet temperature [K]

        T[i] = T_out
        E += dE

    q = E / ( 4 * W * L * 10000 )
    
    if make_fields:
        return np.linspace(0, L, N_ELE), T
    
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

    def __init__(self, T_in, T_w, Q, geometry, fluid):
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
        
    def solve(self, make_fields=False):
        # Returns the heat flux, pressure drop, and output temperature
        # using the naive method
        #
        # Returns
        # q : the heat transfer [W/cm^3]
        # dP : the pressure loss [Pa]
        # T_out : the outlet temperature [K]
        
        return naive_model(self.T_in,
                            self.T_w,
                            self.Q,
                            **self.geometry.__dict__,
                            **self.fluid.__dict__,
                            make_fields=make_fields)


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
