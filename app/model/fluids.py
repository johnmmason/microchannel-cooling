#!/bin/python3
import taichi as ti

@ti.data_oriented
class Fluid:
    def __init__(self, **var):
        # Initialize Fluid
        #
        # rho : density [kg/m^3]
        # mu : viscosity [Pa*s]
        # cp : heat capacity [J/kg*K]
        # k : thermal conductivity [W/m*K]
        
        for key, value in var.items(): # easy way to set attributes
            setattr(self, key, value)
            
        self.Pr = self.mu * self.cp / self.k # Prandtl number
            
water = Fluid(rho = 997, # density of water [kg/m^3]
              mu = 0.00089, # viscosity of water [Pa*s]
              cp = 4180, # heat capacity of water [J/kg*K]
              k = 0.606, # thermal conductivity of water [W/m*K]
              T_boiling_point = 373.15, # boiling point of water [K]
              latent_heat_of_vaporization = 2260000, # latent heat of vaporization of water [J/kg]
              ) 

ethylene_glycol = Fluid(rho = 1115, # density of antifreeze [kg/m^3]
                        mu = 0.0161, # viscosity of antifreeze [Pa*s]
                        cp = 2420,  # heat capacity of antifreeze [J/kg*K]
                        k =  0.25,  # thermal conductivity of antifreeze [W/m*k]
                        T_boiling_point = 470.15, # boiling point of antifreeze [K]
                        latent_heat_of_vaporization = 2513000, # latent heat of vaporization of antifreeze [J/kg]
                        )

silicon_dioxide_nanofluid = Fluid(rho = 1500,
                                  mu = 0.00235,
                                  cp = 3100,
                                  k = 0.2526,
                                  T_boiling_point = 470.15,
                                  latent_heat_of_vaporization = 2513000, # same values as ethylene_glycol, since SiO2 is a solid (extremely high boiling point)
                                  ) # https://www.sciencedirect.com/science/article/pii/S0040603117300230, 5% mass fraction

mineral_oil = Fluid(rho = 820,
                    mu = 0.07,
                    cp = 2000,
                    k = 0.14,
                    T_boiling_point = 647.15,
                    latent_heat_of_vaporization = 2260000, # TODO unknown value - need to find
                    )

silicon = Fluid(rho = 2329, # density of silicon [kg/m^3]
                mu = 0, # viscosity of solid silicon [Pa*s] (not needed, but to maintain compatibility)
                cp = 700, # heat capacity of silicon [J/kg*K]
                k = 148, # thermal conductivity of silicon [W/m*K]
                T_boiling_point = 2628.15, # boiling point of silicon [K] (not relevant for solid, but to maintain compatibility)
                latent_heat_of_vaporization = 0, # latent heat of vaporization of solid silicon [J/kg] (not needed, but to maintain compatibility)
                ) 

fluids = [water, ethylene_glycol, silicon_dioxide_nanofluid, mineral_oil]
fluidnames = ['Water', 'Ethylene Glycol', 'SiO2 Nanofluid', 'Mineral Oil']
fluidoptions = [{'label': fluidnames[i], 'value': i} for i in range(len(fluids))]