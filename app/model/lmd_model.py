#!/bin/python3
import taichi as ti
from model.limits import limits
from model.fluids import fluids, Silicon as Si # TODO Si parameters (@longvu)
from model.lmd_fluid import setup_fluid_velocity, calculate_Re, calculate_Nu
from model.lmd_heat_flux import setup_heat_flux
from model.lmd_geometry import Geometry
from model.lmd_heat import setup_heat_resistance

@ti.kernel
def calculate_current(geometry):
    for i in range(geometry.nx-1):
        for j in range(geometry.ny-1):
            for k in range(geometry.nz-1):
                for w in range(geometry.nd):
                    geometry.current[i,j,k,w] = (geometry.temp[i,j,k] - geometry.temp[i+1,j+1,k+1]) / geometry.heat_resistance[i,j,k,w]

@ti.kernel
def propagate_current(fluid, geometry):
    for i in range(geometry.nx-1):
        for j in range(geometry.ny-1):
            for k in range(geometry.nz-1):
                for w in range(geometry.nd):
                    # mdot cp T flow
                    
                    dT = geometry.temp[i+1,j+1,k+1] - geometry.temp[i,j,k]
                    mdot = fluid.rho * geometry.velocity[i,j,k,w] * geometry.interface_area[i,j,k,w]
                    geometry.current[i,j,k,w] += mdot * fluid.cp * dT


@ti.kernel
def calculate_temperature(geometry):
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
               
                flux = geometry.heat_flux[i,j,k] \
                    + geometry.current[i,j,k,0] - geometry.current[i-1,j,k,0] \
                    + geometry.current[i,j,k,1] - geometry.current[i,j-1,k,1] \
                    + geometry.current[i,j,k,2] - geometry.current[i,j,k-1,2]
                
                geometry.temp_next[i] = flux / geometry.heat_capacity[i] + geometry.temp[i]

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
                        
            calculate_current(self.geometry)
            propagate_current(self.fluid,self.geometry) # adjust current to account for fluid motion
            calculate_temperature(self.geometry)
            
            if i % self.update_freq == 0:
                calculate_Nu(self.fluid, self.geometry)
                setup_heat_resistance(self.solid, self.fluid, self.geometry)
    
    
    def solve(self, make_fields=False):
        
        setup_fluid_velocity(self.geometry)
        
        calculate_Re(self.fluid, self.geometry)
        
        setup_heat_flux(self.heat_flux_function, self.geometry)
        
        return self.main(**self.geometry.__dict__,
                         **self.fluid.__dict__,
                         make_fields=make_fields)

