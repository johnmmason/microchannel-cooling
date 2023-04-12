#!/bin/python3
import taichi as ti
from model.limits import limits
from model.fluids import fluids, Silicon as Si # TODO Si parameters (@longvu)

    
class Geometry:
    def __init__(self, **kwargs):
        param = {
            'L_chip': 0.01464,
            'W_chip': 0.0168,
            'H_chip': 0.0001,
            'L_channel': 0.01464,
            'W_channel': 500e-6,
            'H_channel': 50e-6,
            'n_channel': 30,
            'nx': 100, # please fill in the rest of the parameters
        } | kwargs
               
               
                # problem setting
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.it = 0
        self.plot_freq = 2000

        # physical parameters
        # time-integration related
        self.h = h # time-step size
        self.substep = substep # number of substeps
        self.dx = dx # finite difference step size (in space)
        self.dy = dy
        self.dz = dz
        self.nd = 3
        n2 = self.nx * self.ny * self.nz   
            
        # Initialize Geometry - @colenockolds, @longvu, @akhilsadam
        # Nodal
        # example here https://github.com/hejob/taichi-fvm2d-fluid-ns/blob/master/multiblocksolver/block_solver.py
        self.temp = ti.field(ti.f32, shape = n2,) # unrolled to 1-d array
        self.temp_1 = ti.field(ti.f32, shape = n2,) # unrolled to 1-d array
        self.update = ti.field(ti.f32, shape = n2,)
        self.velocity = ti.field(ti.f32, shape = n2,) # from fluid
        self.k = ti.field(ti.f32, shape = n2,) # from geometry
        
        # Resistance / intermediates
        # Fluid @akhilsadam
        # self.p = #
        # self.v = #

        for key, val in param.items():
            setattr(self, key, val)

class MicroChannelCooler:

    def __init__(self, **kwargs):
        # geometry : a Geometry
        # fluid : a Fluid
        # T_in : fluid inlet temperature [K]
        # heat_flux_function : function of (x,y,t) that returns heat flux [W/m^2]
        # Q : fluid flow rate [uL/min]
        param = {
            'T_in': limits['T_in']['init'],
            'heat_flux_function': lambda x,y,t: 0.0, # TODO (@savannahsmith, please add a more realistic default and work with GUI team to figure out how to pass in a function)
            'Q' : limits['Q']['init'], 
            'geometry' : None,
            'fluid' : fluids[0]
        } | kwargs
        
        assert param['geometry'] is not None, "Geometry must be specified"
        
        self.heat_flux_function = param['heat_flux_function']
        
        for key, val in param.items():
            setattr(self, key, val)
        
        
    def setupFluid(self):
        pass # TODO (@akhilsadam)
    
    def setupHeatFlux(self):
        pass
    
    def main(self):
        pass
    
    def solve(self, make_fields=False):
        
        return self.main(**self.geometry.__dict__,
                         **self.fluid.__dict__,
                         make_fields=make_fields)

