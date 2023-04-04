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

ethylene_glycol = Fluid(rho = 1110, # density of ethylene glycol [kg/m^3]
                        mu = 0.0159, # viscosity of ethylene glycol [Pa*s] at 25°C
                        cp = 2420,  # heat capacity of ethylene glycol [J/kg*K]
                        k =  0.254)  # thermal conductivity of ethylene glycol [W/m*k]

silicon_dioxide_nanofluid = Fluid(rho = 1500,
                                  mu = 0.0003,
                                  cp = 3100,
                                  k = 2.5)

mineral_oil = Fluid(rho = 820,
                    mu = 0.07,
                    cp = 2000,
                    k = 0.14)
