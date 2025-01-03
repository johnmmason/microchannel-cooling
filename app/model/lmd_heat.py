import taichi as ti
from model.lmd_resistance_functions import solid_to_solid, solid_to_liquid, liquid_to_liquid
# these functions can be used in a taichi kernel
# args: (solid/fluid, geometry, i1,j1,k1, i2,j2,k2, ie,je,ke,) (the two nodes to calculate the resistance between, and then the element index, note order-independent)


@ti.kernel
def setup_heat_resistance(solid: ti.template(), fluid: ti.template(), geometry: ti.template()): 
    ti.loop_config(parallelize=8, block_dim=16)
    # fill in the heat_resist array from lmd_geometry as in lmd_fluid.py
    # @longvu
    for i, j, k, w in ti.ndrange(geometry.nx, geometry.ny, geometry.nz, geometry.nd):
        i2, j2, k2 = i + (w == 0), j + (w == 1), k + (w == 2)
        ie, je, ke = i, j, k

        if geometry.interfaces[ie, je, ke, w] == 0:  # Solid-solid interface
            geometry.heat_resist[i, j, k, w] = solid_to_solid(solid, geometry, i, j, k, i2, j2, k2, ie, je, ke, w)
        elif geometry.interfaces[ie, je, ke, w] == 1:  # Solid-fluid interface
            sl_bit = 0
            if geometry.isfluid[i, j, k] != 0:
                sl_bit = 1
            geometry.heat_resist[i, j, k, w] = solid_to_liquid(fluid, geometry, i, j, k, i2, j2, k2, ie, je, ke, w, sl_bit)
        elif geometry.interfaces[ie, je, ke, w] == 2:  # Fluid-fluid interface
            geometry.heat_resist[i, j, k, w] = liquid_to_liquid(fluid, geometry, i, j, k, i2, j2, k2, ie, je, ke, w)
    

@ti.kernel
def setup_nodal_heat_capacity(solid: ti.template(), fluid: ti.template(), geometry: ti.template()):
    # fill in the nodal_heat_capacity array (so basically m*Cp per node), use the volume field from lmd_geometry
    # TODO @longvu
    for i, j, k in ti.ndrange(geometry.nx, geometry.ny, geometry.nz):
        if geometry.isfluid[i, j, k] == 0:  # Fluid node
            geometry.heat_capacity[i, j, k] = fluid.rho * fluid.cp * geometry.volume[i, j, k]
        else:  # Solid node
            geometry.heat_capacity[i, j, k] = solid.rho * solid.cp * geometry.volume[i, j, k]
            
@ti.kernel
def setup_temperature(geometry: ti.template()):
    for i, j, k in ti.ndrange(geometry.nx, geometry.ny, geometry.nz):
        geometry.temp[i, j, k] = 293.15 # 20 deg C
