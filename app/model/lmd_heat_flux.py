import taichi as ti

def setup_heat_flux(heat_flux_function, geometry): 
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
                if geometry.isfluid[i,j,k] != 1: # if not fluid
                    x,y,z = geometry.ijk_to_xyz_host(i,j,k)
                    geometry.heat_flux[i,j,k] = heat_flux_function(x,y,z) / geometry.volume[i,j,k]
                    
if __name__ == '__main__':
    from lmd_geometry import Geometry
    ti.init()
    g = Geometry()
    setup_heat_flux(lambda x,y,z: 5.0, g)
    print('lmd_heat_flux.py succeeded!')