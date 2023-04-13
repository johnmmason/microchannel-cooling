#@akhilsadam
import taichi as ti


@ti.func
def solid_to_liquid(self,i1,i2,ie):
    # Efficient Microchannel Cooling of Multiple Power Devices with Compact Flow Distribution for High Power-Density Converters : Remco van Erp, et al. 2019
    # R_conv = 1/(h*A), (A is contact area between solid and liquid)
    # R_int, R_j-c are negligible (as in paper)
    # h = Nu * k / D 
    
    # one of Nu should be 0 / low since that is the solid side
    Nu = ti.max(self.Nu[i1], self.Nu[i2])
    h = Nu * self.fluid.k / self.geometry.D_channel
    A = self.geometry.interfaceArea[ie]
    return 1/(h*A)

@ti.func
def solid_to_solid(self,i1,i2,ie):
    p1 = self.geometry.i_to_xyz(i1)
    p2 = self.geometry.i_to_xyz(i2)
    d = ti.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
    return d/(self.solid.k * self.geometry.interfaceArea[ie])

@ti.func
def liquid_to_liquid(self,i1,i2,ie):
    p1 = self.geometry.i_to_xyz(i1)
    p2  = self.geometry.i_to_xyz(i2)
    d = ti.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
    return d/(self.fluid.k * self.geometry.interfaceArea[ie])
    
    
    

    