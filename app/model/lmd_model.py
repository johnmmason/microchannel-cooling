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
                    i2, j2, k2 = i + (w == 0), j + (w == 1), k + (w == 2)
                    geometry.current[i,j,k,w] += (geometry.temp[i,j,k] - geometry.temp[i2,j2,k2]) / geometry.heat_resist[i,j,k,w]

@ti.kernel
def propagate_current(T_in: ti.f32, fluid: ti.template(), geometry: ti.template()):
    # inlet # check this - not sure if it's correct
    for j in range(geometry.ny-1):
        for k in range(geometry.nz-1):
            # inlet
            dm = fluid.rho * geometry.velocity[0,j,k,0] * geometry.interface_area[0,j,k,0] # should really be [-1,j,k,0], but this works since that is not set (auto set to 0)
            geometry.current[-1,j,k,0] = dm * fluid.cp * T_in
            
    for i in range(geometry.nx-1):
        for j in range(geometry.ny-1):
            for k in range(geometry.nz-1):
                for w in range(geometry.nd):
                    # m cp T flow
                    T = geometry.temp[i,j,k]
                    dm = fluid.rho * geometry.velocity[i,j,k,w] * geometry.interface_area[i,j,k,w]
                    geometry.current[i,j,k,w] += dm * fluid.cp * T
    # outlet
    lnx = geometry.nx-1 
    for j in range(geometry.ny-1):
        for k in range(geometry.nz-1):
            T = geometry.temp[geometry.nx-1,j,k] # (at the outlet, the temperature is the same as the last node, since we don't care about exit heat balance...)
            dm = fluid.rho * geometry.velocity[geometry.nx-1,j,k,0] * geometry.interface_area[lnx,j,k,0]
            geometry.current[lnx,j,k,0] = dm * fluid.cp * T
            
    
@ti.kernel
def zero_current(geometry: ti.template()):
    for i in ti.grouped(geometry.current):
        geometry.current[i] = 0.0


@ti.kernel
def calculate_temperature(geometry: ti.template()):
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
               
                flux = geometry.heat_flux[i,j,k] \
                    - geometry.current[i,j,k,0] + geometry.current[i-1,j,k,0] \
                    - geometry.current[i,j,k,1] + geometry.current[i,j-1,k,1] \
                    - geometry.current[i,j,k,2] + geometry.current[i,j,k-1,2]
                # print(flux)
                geometry.temp_next[i,j,k] = (flux * (geometry.h / geometry.substep) / geometry.heat_capacity[i,j,k]) + geometry.temp[i,j,k]

@ti.kernel
def commit(geometry: ti.template()):
    geometry.sum_temp[0] = 0.0
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
                new_T = ti.min(ti.max(geometry.temp_next[i,j,k],273.15),373.15)
                geometry.sum_temp[0] += ti.abs(new_T - geometry.temp[i,j,k])
                geometry.temp[i,j,k] = new_T

class MicroChannelCooler:

    def __init__(self, **kwargs):
        # geometry : a Geometry
        # fluid : a Fluid
        # T_in : fluid inlet temperature [K]
        # heat_flux_function : function of (x,y,t) that returns heat flux [W/m^2]
        # Q : fluid flow rate [uL/min]
        param = {
            'T_in': limits['T_in']['init'],
            'heat_flux_function': lambda x,y: 5000, # TODO (@savannahsmith, please add a more realistic default and work with GUI team to figure out how to pass in a function)
            'Q' : limits['Q']['init'], 
            'geometry' : None,
            'fluid' : fluids[0],
            'solid': si,
            'nit': 400000,
        } 
        param.update(kwargs)
        
        # unit conversions
        param['T_in'] += limits['T_in']['shift']
        param['Q'] *= (15/9)/(10**8) # uL/min -> m^3/s
        hff = param['heat_flux_function']
        param['heat_flux_function'] = lambda x,y: hff(x,y) * (10**4) # W/cm^2 -> W/m^2
        
        
        
        assert param['geometry'] is not None, "Geometry must be specified"
        
        self.heat_flux_function = param['heat_flux_function']
        
        for key, val in param.items():
            setattr(self, key, val)                   
                    
    def main(self, **kwargs):  # sourcery skip: extract-duplicate-method
                        
        setup_fluid_velocity(self.Q, self.geometry)
        calculate_Re(self.fluid, self.geometry)
        setup_heat_flux(self.heat_flux_function, self.geometry)
        setup_nodal_heat_capacity(self.solid, self.fluid, self.geometry)
        setup_temperature(self.geometry)
    
        dt0 = 500.0
        for it in tqdm(range(self.nit)):
            calculate_Nu(self.fluid, self.geometry)
            setup_heat_resistance(self.solid, self.fluid, self.geometry)

            for _ in range(self.geometry.substep):
                zero_current(self.geometry)
                calculate_current(self.geometry)
                propagate_current(self.T_in, self.fluid,self.geometry) # adjust current to account for fluid motion
                calculate_temperature(self.geometry)
                commit(self.geometry)
                dt = self.geometry.sum_temp[0]
                
            if it==1:
                dt0 = dt
            if it > 2 and (dt < 0.01*dt0 or dt < 400/self.geometry.nn):
                print('Converged in', it+1, 'iterations, with final step-size dT =', float(dt))
                return
            elif it > self.nit*0.01 and dt/dt0 > 0.9:
                if dt/dt0 < 1.5:
                    print('Failed any possible converge in', it+1, 'iterations, with constant step-size dT =', float(dt), '\n Please check your timestep, spatial resolution, and heat-flux magnitude.')
                else:
                    print('Exploded within in', it+1, 'iterations, with step-size dT =', float(dt), '\n Please check your timestep, spatial resolution, and heat-flux magnitude to improve stability.')
                return
            print('Iteration', it+1, 'completed with step-size dT =', float(dt))
            
                
                
                
    
    
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
    
    # window = ti.ui.Window("Lumped Mass Model", (768, 768))
    # canvas = window.get_canvas()
    # scene = ti.ui.Scene()
    # camera = ti.ui.Camera()
    # camera.position(5, 2, 2)
    
    # particles_pos = ti.Vector.field(3, dtype=ti.f32, shape=(g.nx*g.ny*g.nz))
    # c = ti.Vector.field(3, dtype=ti.f32, shape=(g.nx*g.ny*g.nz))
    
    # @ti.kernel
    # def make_pos(f:ti.template(),c:ti.template(),g:ti.template(),item:ti.template(),tmin:ti.f32, trange:ti.f32):
    #     for i in range(g.nx):
    #         for j in range(g.ny):
    #             for k in range(g.nz):
    #                 x,y,z = g.ijk_to_xyz(i, j, k)
    #                 f[i*g.ny*g.nz + j*g.nz +k] = ti.Vector([x*1000,y*1000,z*1000])
    #                 t = float(item[i,j,k]) - tmin
    #                 t /= trange
    #                 b = 1 - t
    #                 c[i*g.ny*g.nz + j*g.nz +k] = ti.Vector([t,.5,b])
                    
    # # make_pos(particles_pos,c,g,g.temp,273.15,100)   
    # # make_pos(particles_pos,c,g,g.heat_flux,0.0,0.0125) # clamping out everything above 0.0125
    # # make_pos(particles_pos,c,g,g.interface_area,0.0,100e-10)
    # make_pos(particles_pos,c,g,g.heat_capacity,0.0,1e-7)
    # # make_pos(particles_pos,c,g,g.isfluid,0,3.0)    
    # while window.running:
    #     camera.track_user_inputs(window, movement_speed=0.01, hold_key=ti.ui.RMB)
    #     scene.set_camera(camera)
    #     scene.ambient_light((0.8, 0.8, 0.8))
    #     scene.point_light(pos=(0.5, 1.5, 1.5), color=(1, 1, 1))

    #     scene.particles(particles_pos, per_vertex_color=c, radius = 0.01)
    #     # Draw 3d-lines in the scene
    #     canvas.scene(scene)
    #     window.show()
    
    import numpy as np
    data = g.temp.to_numpy()[:,:,:].reshape(g.nx,g.ny,g.nz) - 273.15
    
    # @ti.kernel
    # def shift(geo:ti.template()):
    #     for z in range(-1,geo.nz+1):
    #         print(geo.interfaces[0,0,z,0], geo.interface_area[0,0,z,0]*1.0e11, \
    #               geo.interface_area[0,0,z,1]*1.0e11, \
    #               geo.interface_area[0,0,z,2]*1.0e11)
    # #     # for i in range(g.nx):
    # #     #     for j in range(g.ny):
    # #     #         for k in range(g.nz):
    # #     #             for w in range(g.nd):
    # #     #                 item[i,j,k,w] = cur[i-1,j-1,k-1,w]
    
    # # cur = ti.field(ti.f32, shape=(g.nx+1,g.ny+1,g.nz+1,g.nd))
    # shift(g)
    # data = cur.to_numpy()[:,:,:,0]   
    # data = data[0:-1,1:,1:].reshape(g.nx,g.ny,g.nz)
    # data = g.temp_next.to_numpy()[:,:,:].reshape(g.nx,g.ny,g.nz) - g.temp.to_numpy()[:,:,:].reshape(g.nx,g.ny,g.nz)
    # print(data[:,:,:])
    # print(np.min(data), np.mean(data), np.std(data), np.max(data))
    import pyvista as pv
    pl = pv.Plotter()
    pl.open_gif(f"../../../output_3d.gif")   
    # pl.camera.position = (-1.1, -1.5, 0.0)
    # pl.camera.focal_point = (50.0, 50.0, 0.0)
    # pl.camera.up = (1.0, 0.0, 1.0)
    pl.add_volume(data, cmap="jet", opacity=0.5)
    pl.write_frame()
    pl.close()