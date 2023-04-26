import taichi as ti

def setup_heat_flux(heat_flux_function, geometry): 
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            vz = 0.0
            for k in range(geometry.nz):
                if geometry.isfluid[i,j,k] != 0: # if not fluid
                    vz += geometry.volume[i,j,k]

            if vz > 0.0:
                a = geometry.interface_area[i,j,0,2] # XY plane area
                for k in range(geometry.nz):
                    if geometry.isfluid[i,j,k] != 0: # if not fluid
                        x,y,z = geometry.ijk_to_xyz_host(i,j,k)
                        x0 = x / geometry.L_chip - 0.5
                        y0 = y / geometry.W_chip - 0.5
                        geometry.heat_flux[i,j,k] = heat_flux_function(x0,y0) * a * geometry.volume[i,j,k] / vz
                        #assumes W/m^2
            else:
                print('Warning: no volume for heat flux at i,j = ', i, j)
                    
if __name__ == '__main__':
    from lmd_geometry import Geometry
    ti.init()
    g = Geometry()
    setup_heat_flux(lambda x,y: 5.0, g)
    print('lmd_heat_flux.py succeeded!')