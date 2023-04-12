import taichi as ti
from model.lmd_resistance_functions import solid_to_solid, solid_to_fluid, fluid_to_fluid
# only takes in self (for now ) - these functions can be used in a taichi kernel


@ti.kernel
def setup_heat_resistance(self): 
    # fill in the heat_resist array from lmd_geometry as in lmd_fluid.py
    # TODO @longvu
    pass
    