#!/bin/python3
import taichi as ti
from model.limits import limits
from model.fluids import fluids, Silicon as Si # TODO Si parameters (@longvu)
from model.lmd_fluid import setup_fluid, calculate_Re, calculate_Nu
from model.lmd_heat_flux import setup_heat_flux
from model.lmd_geometry import Geometry
from model.lmd_heat import setup_heat_resistance



class MicroChannelCooler:

    def __init__(self, **kwargs):
        # geometry : a Geometry
        # fluid : a Fluid
        # T_in : fluid inlet temperature [K]
        # heat_flux_function : function of (x,y,t) that returns heat flux [W/m^2]
        # Q : fluid flow rate [uL/min]
        param = {
            'T_in': limits['T_in']['init'],
            'heat_flux_function': lambda x,y,t: 5.0, # TODO (@savannahsmith, please add a more realistic default and work with GUI team to figure out how to pass in a function)
            'Q' : limits['Q']['init'], 
            'geometry' : None,
            'fluid' : fluids[0],
            'solid': Si,
            'nit': 100,
            'update_frequency': 10,
        } | kwargs
        
        assert param['geometry'] is not None, "Geometry must be specified"
        
        self.heat_flux_function = param['heat_flux_function']
        
        for key, val in param.items():
            setattr(self, key, val)                   
                    
    def main(self):
        
        for i in self.nit:
            
            self.calculate_Nu()
            
            self.step()
            
            if i % self.update_freq == 0:
                self.update()
    
    
    def solve(self, make_fields=False):
        
        self.setup_fluid()
        
        self.calculate_Re()
        
        return self.main(**self.geometry.__dict__,
                         **self.fluid.__dict__,
                         make_fields=make_fields)

