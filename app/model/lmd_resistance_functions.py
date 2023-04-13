#@akhilsadam
import taichi as ti


@ti.func
def solid_to_liquid(fluid, geometry, i1,i2,ie):
    # Efficient Microchannel Cooling of Multiple Power Devices with Compact Flow Distribution for High Power-Density Converters : Remco van Erp, et al. 2019
    # R_conv = 1/(h*A), (A is contact area between solid and liquid)
    # R_int, R_j-c are negligible (as in paper)
    # h = Nu * k / D 
    
    # one of Nu should be 0 / low since that is the solid side
    Nu = ti.max(geometry.Nu[i1], geometry.Nu[i2])
    h = Nu * fluid.k / geometry.D_channel
    A = geometry.interfaceArea[ie]
    return 1/(h*A)

@ti.func
def solid_to_solid(solid,geometry,i1,i2,ie):
    p1 = geometry.i_to_xyz(i1)
    p2 = geometry.i_to_xyz(i2)
    d = ti.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
    return d/(solid.k * geometry.interfaceArea[ie])

@ti.func
def liquid_to_liquid(fluid,geometry,i1,i2,ie):
    p1 = geometry.i_to_xyz(i1)
    p2  = geometry.i_to_xyz(i2)
    d = ti.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
    return d/(fluid.k * geometry.interfaceArea[ie])
    
    
    

    