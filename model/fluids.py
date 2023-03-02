#!/bin/python3

class Fluid:
    def __init__(self, rho, mu, cp, k):
        # Initialize Fluid
        #
        # rho : density [kg/m^3]
        # mu : viscosity [Pa*s]
        # cp : heat capacity [J/kg*K]
        # k : thermal conductivity [W/m*K]
        
        self.rho = rho 
        self.mu = mu 
        self.cp = cp 
        self.k = k

water = Fluid(rho = 997, # density of water [kg/m^3]
              mu = 0.00089, # viscosity of water [Pa*s]
              cp = 4180, # heat capacity of water [J/kg*K]
              k = 0.606) # thermal conductivity of water [W/m*K]
