import taichi as ti
from model.lmd_resistance_functions import solid_to_solid, solid_to_fluid, fluid_to_fluid
# these functions can be used in a taichi kernel
# args: (self, i1,j1,k1, i2,j2,k2, ie,je,ke) (the two nodes to calculate the resistance between, and then the element index, note order-independent)


@ti.kernel
def setup_heat_resistance(self): 
    # fill in the heat_resist array from lmd_geometry as in lmd_fluid.py
    # TODO @longvu
    pass
    