#!/bin/python3
if __name__ == '__main__':
    import sys
    sys.path.append("..")

import taichi as ti
from model.limits import limits
from model.fluids import fluids, silicon as si # TODO Si parameters (@longvu)
from model.lmd_fluid import setup_fluid_velocity, calculate_Re, calculate_Nu
from model.lmd_heat_flux import setup_heat_flux
from model.lmd_geometry import Geometry
from model.lmd_heat import setup_heat_resistance, setup_nodal_heat_capacity, setup_temperature
from tqdm import tqdm

@ti.kernel
def calculate_current(geometry: ti.template()):
    for i in range(geometry.nx-1):
        for j in range(geometry.ny-1):
            for k in range(geometry.nz-1):
                for w in range(geometry.nd):
                    geometry.current[i,j,k,w] = (geometry.temp[i,j,k] - geometry.temp[i+1,j+1,k+1]) / geometry.heat_resist[i,j,k,w]

@ti.kernel
def propagate_current(T_in: ti.f32, fluid: ti.template(), geometry: ti.template()):
    # inlet
    for j in range(geometry.ny-1):
        for k in range(geometry.nz-1):
            # inlet
            dT = T_in - geometry.temp[-1,j,k] # (at the inlet, the fluid mixes with the first node, so the temperature is the delta between the inlet and the first node)
            m = fluid.rho * geometry.velocity[-1,j,k,0] * geometry.interface_area[-1,j,k,0] * geometry.h / geometry.substep
            geometry.current[-1,j,k,0] += m * fluid.cp * dT
            
    for i in range(geometry.nx-1):
        for j in range(geometry.ny-1):
            for k in range(geometry.nz-1):
                for w in range(geometry.nd):
                    # m cp T flow
                    dT = geometry.temp[i+1,j+1,k+1] - geometry.temp[i,j,k]
                    m = fluid.rho * geometry.velocity[i,j,k,w] * geometry.interface_area[i,j,k,w] * geometry.h / geometry.substep
                    geometry.current[i,j,k,w] += m * fluid.cp * dT
    # outlet
    lnx = geometry.nx-1
    for j in range(geometry.ny-1):
        for k in range(geometry.nz-1):
            dT = geometry.temp[geometry.nx-1,j,k] # (at the outlet, the temperature is the same as the last node, since we don't care about exit heat balance...)
            m = fluid.rho * geometry.velocity[lnx,j,k,0] * geometry.interface_area[lnx,j,k,0] * geometry.h / geometry.substep
            geometry.current[lnx,j,k,0] += m * fluid.cp * dT
            
            
    



@ti.kernel
def calculate_temperature(geometry: ti.template()):
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
               
                flux = geometry.heat_flux[i,j,k] \
                    + geometry.current[i,j,k,0] - geometry.current[i-1,j,k,0] \
                    + geometry.current[i,j,k,1] - geometry.current[i,j-1,k,1] \
                    + geometry.current[i,j,k,2] - geometry.current[i,j,k-1,2]
                
                geometry.temp_next[i,j,k] = (flux * (geometry.h / geometry.substep) / geometry.heat_capacity[i,j,k]) + geometry.temp[i,j,k]

@ti.kernel
def commit(geometry: ti.template()):
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
                geometry.temp[i,j,k] = ti.min(ti.max(geometry.temp_next[i,j,k],273.15),373.15)

class MicroChannelCooler:

    def __init__(self, **kwargs):
        # geometry : a Geometry
        # fluid : a Fluid
        # T_in : fluid inlet temperature [K]
        # heat_flux_function : function of (x,y,t) that returns heat flux [W/m^2]
        # Q : fluid flow rate [uL/min]
        param = {
            'T_in': limits['T_in']['init'],
            'heat_flux_function': lambda x,y: 0.250, # TODO (@savannahsmith, please add a more realistic default and work with GUI team to figure out how to pass in a function)
            'Q' : limits['Q']['init'], 
            'geometry' : None,
            'fluid' : fluids[0],
            'solid': si,
            'nit': 100,
        } 
        param.update(kwargs)
        
        # unit conversions
        param['T_in'] += limits['T_in']['shift']
        param['Q'] *= (15/9)/(10**8) # uL/min -> m^3/s
        hff = param['heat_flux_function']
        param['heat_flux_function'] = lambda x,y: hff(x,y) * (10**4) # W/m^2 -> W/cm^2
        
        
        
        assert param['geometry'] is not None, "Geometry must be specified"
        
        self.heat_flux_function = param['heat_flux_function']
        
        for key, val in param.items():
            setattr(self, key, val)                   
                    
    def main(self, **kwargs):
                        
        setup_fluid_velocity(self.Q, self.geometry)
        calculate_Re(self.fluid, self.geometry)
        setup_heat_flux(self.heat_flux_function, self.geometry)
        setup_nodal_heat_capacity(self.solid, self.fluid, self.geometry)
        setup_temperature(self.geometry)

        for _ in tqdm(range(self.nit)):
            calculate_Nu(self.fluid, self.geometry)
            setup_heat_resistance(self.solid, self.fluid, self.geometry)
            for _ in range(self.geometry.substep):
                calculate_current(self.geometry)
                propagate_current(self.T_in, self.fluid,self.geometry) # adjust current to account for fluid motion
                calculate_temperature(self.geometry)
                commit(self.geometry)
    
    
    def solve(self, make_fields=False):
        
        self.main(**self.geometry.__dict__,
                    **self.fluid.__dict__)
        
        # Please output relevant estimates here; I'm not sure what we need to output - esp. re. complete field data for CFD (which will be output if make_fields is True)
        # temp, heat_flux over length / slice along z-axis
        # maybe a 3D visualization.
        
if __name__ == '__main__':
    
    ti.init(ti.cpu, kernel_profiler=False)
    g = Geometry()
    m = MicroChannelCooler(geometry=g)
    m.solve()
    print('lmd_model.py succeeded!')
    # ti.profiler.print_kernel_profiler_info()
    
    window = ti.ui.Window("Lumped Mass Model", (768, 768))
    canvas = window.get_canvas()
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()
    camera.position(5, 2, 2)
    
    particles_pos = ti.Vector.field(3, dtype=ti.f32, shape=(g.nx*g.ny*g.nz))
    c = ti.Vector.field(3, dtype=ti.f32, shape=(g.nx*g.ny*g.nz))
    
    @ti.kernel
    def make_pos(f:ti.template(),c:ti.template(),g:ti.template(),item:ti.template(),tmin:ti.f32, trange:ti.f32):
        for i in range(g.nx):
            for j in range(g.ny):
                for k in range(g.nz):
                    x,y,z = g.ijk_to_xyz(i, j, k)
                    f[i*g.ny*g.nz + j*g.nz +k] = ti.Vector([x*1000,y*1000,z*1000])
                    t = float(item[i,j,k]) - tmin
                    t /= trange
                    b = 1 - t
                    c[i*g.ny*g.nz + j*g.nz +k] = ti.Vector([t,.5,b])
                    
    make_pos(particles_pos,c,g,g.temp,273.15,100)   
    # make_pos(particles_pos,c,g,g.heat_flux,0.0,0.0125) # clamping out everything above 0.0125
    # make_pos(particles_pos,c,g,g.isfluid,0,3.0)    
    while window.running:
        camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)
        scene.set_camera(camera)
        scene.ambient_light((0.8, 0.8, 0.8))
        scene.point_light(pos=(0.5, 1.5, 1.5), color=(1, 1, 1))

        scene.particles(particles_pos, per_vertex_color=c, radius = 0.01)
        # Draw 3d-lines in the scene
        canvas.scene(scene)
        window.show()
    
    # import pyvista as pv
    # pl = pv.Plotter()
    # pl.open_gif(f"../../../output_3d.gif")   
    # # pl.camera.position = (-1.1, -1.5, 0.0)
    # # pl.camera.focal_point = (50.0, 50.0, 0.0)
    # # pl.camera.up = (1.0, 0.0, 1.0)
    # data = g.temp.to_numpy()[:,:,:].reshape(g.nx,g.ny,g.nz) - 273.15
    # print(data)
    # pl.add_volume(data, cmap="jet", opacity=0.5)
    # pl.write_frame()
    # pl.close()