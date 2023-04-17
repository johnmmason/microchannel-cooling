import taichi as ti

@ti.kernel
def setup_heat_flux(heat_flux_function, geometry): 
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
                if geometry.isfluid[i,j,k]:
                    (x,y,z) =  geometry.ijk_to_xyz[i,j,k]
                    geometry.heat_flux[x,y,z] = # heat_flux_function(lambda) not sure how to implement this with what is currently on github
    pass