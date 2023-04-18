#@akhilsadam
import taichi as ti


@ti.func
def solid_to_liquid(fluid: ti.template(), geometry: ti.template(),
                    i1:ti.i32,j1:ti.i32,k1:ti.i32,i2:ti.i32,j2:ti.i32,k2:ti.i32,ie:ti.i32,je:ti.i32,ke:ti.i32,we:ti.i32):
    # Efficient Microchannel Cooling of Multiple Power Devices with Compact Flow Distribution for High Power-Density Converters : Remco van Erp, et al. 2019
    # R_conv = 1/(h*A), (A is contact area between solid and liquid)
    # R_int, R_j-c are negligible (as in paper)
    # h = Nu * k / D 
    
    # one of Nu should be 0 / low since that is the solid side
    Nu = ti.max(geometry.Nu[i1,j1,k1], geometry.Nu[i2,j2,k2])
    h = Nu * fluid.k / geometry.D_channel
    A = geometry.interface_area[ie,je,ke,we]
    return 1/(h*A)

@ti.func
def solid_to_solid(solid: ti.template(),geometry: ti.template(),
                   i1:ti.i32,j1:ti.i32,k1:ti.i32,i2:ti.i32,j2:ti.i32,k2:ti.i32,ie:ti.i32,je:ti.i32,ke:ti.i32,we:ti.i32):
    p1 = geometry.ijk_to_xyz(i1,j1,k1)
    p2 = geometry.ijk_to_xyz(i2,j2,k2)
    d = ti.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
    return d/(solid.k * geometry.interface_area[ie,je,ke,we])

@ti.func
def liquid_to_liquid(fluid: ti.template(),geometry: ti.template(),
                     i1:ti.i32,j1:ti.i32,k1:ti.i32,i2:ti.i32,j2:ti.i32,k2:ti.i32,ie:ti.i32,je:ti.i32,ke:ti.i32,we:ti.i32):
    p1 = geometry.ijk_to_xyz(i1,j1,k1)
    p2  = geometry.ijk_to_xyz(i2,j2,k2)
    d = ti.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
    return d/(fluid.k * geometry.interface_area[ie,je,ke,we])
    
    
    

    