#!/bin/python3
if __name__ == '__main__':
    import sys
    sys.path.append("..")

import taichi as ti
from model.limits import limits
from model.fluids import fluids, silicon as si # TODO Si parameters (@longvu)
from model.lmd_fluid import setup_fluid_velocity, calculate_Re, calculate_Nu
from model.lmd_heat_flux import setup_heat_flux
from model.lmd_geometry import Geometry
from model.lmd_heat import setup_heat_resistance, setup_nodal_heat_capacity
from tqdm import tqdm

@ti.kernel
def calculate_current(geometry: ti.template()):
    for i in range(geometry.nx-1):
        for j in range(geometry.ny-1):
            for k in range(geometry.nz-1):
                for w in range(geometry.nd):
                    geometry.current[i,j,k,w] = (geometry.temp[i,j,k] - geometry.temp[i+1,j+1,k+1]) / geometry.heat_resist[i,j,k,w]

@ti.kernel
def propagate_current(fluid: ti.template(), geometry: ti.template()):
    for i in range(geometry.nx-1):
        for j in range(geometry.ny-1):
            for k in range(geometry.nz-1):
                for w in range(geometry.nd):
                    # m cp T flow
                    
                    dT = geometry.temp[i+1,j+1,k+1] - geometry.temp[i,j,k]
                    m = fluid.rho * geometry.velocity[i,j,k,w] * geometry.interface_area[i,j,k,w] * geometry.h / geometry.substep
                    geometry.current[i,j,k,w] += m * fluid.cp * dT


@ti.kernel
def calculate_temperature(geometry: ti.template()):
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
               
                flux = geometry.heat_flux[i,j,k] \
                    + geometry.current[i,j,k,0] - geometry.current[i-1,j,k,0] \
                    + geometry.current[i,j,k,1] - geometry.current[i,j-1,k,1] \
                    + geometry.current[i,j,k,2] - geometry.current[i,j,k-1,2]
                
                geometry.temp_next[i,j,k] = (flux * (geometry.h / geometry.substep) / geometry.heat_capacity[i,j,k]) + geometry.temp[i,j,k]

@ti.kernel
def commit(geometry: ti.template()):
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
                geometry.temp[i,j,k] = geometry.temp_next[i,j,k]

class MicroChannelCooler:

    def __init__(self, **kwargs):
        # geometry : a Geometry
        # fluid : a Fluid
        # T_in : fluid inlet temperature [K]
        # heat_flux_function : function of (x,y,t) that returns heat flux [W/m^2]
        # Q : fluid flow rate [uL/min]
        param = {
            'T_in': limits['T_in']['init'],
            'heat_flux_function': lambda x,y,z: 5.0, # TODO (@savannahsmith, please add a more realistic default and work with GUI team to figure out how to pass in a function)
            'Q' : limits['Q']['init'], 
            'geometry' : None,
            'fluid' : fluids[0],
            'solid': si,
            'nit': 1,
        } 
        param.update(kwargs)
        
        assert param['geometry'] is not None, "Geometry must be specified"
        
        self.heat_flux_function = param['heat_flux_function']
        
        for key, val in param.items():
            setattr(self, key, val)                   
                    
    def main(self, **kwargs):
                        
        setup_fluid_velocity(self.Q, self.geometry)
        calculate_Re(self.fluid, self.geometry)
        setup_heat_flux(self.heat_flux_function, self.geometry)
        setup_nodal_heat_capacity(self.solid, self.fluid, self.geometry)

        for _ in tqdm(range(self.nit)):
            calculate_Nu(self.fluid, self.geometry)
            setup_heat_resistance(self.solid, self.fluid, self.geometry)
            for _ in range(self.geometry.substep):
                calculate_current(self.geometry)
                propagate_current(self.fluid,self.geometry) # adjust current to account for fluid motion
                calculate_temperature(self.geometry)
                commit(self.geometry)
    
    
    def solve(self, make_fields=False):
        
        self.main(**self.geometry.__dict__,
                    **self.fluid.__dict__)
        
        # @johnmatthewmason - please output relevant estimates here; I'm not sure what we need to output - esp. re. complete field data for CFD (which will be output if make_fields is True)

if __name__ == '__main__':
    
    ti.init()
    g = Geometry()
    m = MicroChannelCooler(geometry=g)
    m.solve()
    print('lmd_model.py succeeded!')
    
    import pyvista as pv
    pl = pv.Plotter()
    pl.open_gif(f"../../../output_3d.gif")   
    data = g.temp.to_numpy().reshape(g.nx,g.ny,g.nz) 
    print(data)
    pl.add_volume(data, cmap="jet", clim=[273.15,373.15])
    pl.write_frame()
    pl.close()