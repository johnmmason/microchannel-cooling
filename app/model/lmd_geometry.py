import taichi as ti    

@ti.data_oriented
class Geometry:
    def __init__(self, **kwargs):
        param = {
            'L_chip': 0.01464, 'W_chip': 0.0168, 'H_chip': 0.0001,
            'L_channel': 0.01464, 'W_channel': 500e-6, 'H_channel': 50e-6,
            'n_channel': 30,
            'nx': 100, 'ny': 122, 'nz': 4,
            'h': 1e-3, 'substep': 1,
        } 
        param.update(kwargs)
        
        for key, val in param.items():
            setattr(self, key, val)

        # real world measurements
        self.L_chip = param['L_chip']
        self.W_chip = param['W_chip']
        self.H_chip = param['H_chip']
        self.L_channel = param['L_channel']
        self.W_channel = param['W_channel']
        self.H_channel = param['H_channel']
               
        # problem setting
        self.nx = param['nx']
        self.ny = param['ny']
        self.nz = param['nz']

        # physical parameters
        # time-integration related
        self.h = param['h'] # time-step size
        self.substep = param['substep'] # number of substeps

        self.nd = 3
        nodes = (self.nx,self.ny,self.nz)

        self.cell_L = param['L_chip']/self.nx
        self.cell_H = (param['H_channel']/2)
        self.solid_cell_W = (param['W_chip'] - param['n_channel'] * (param['W_channel'])) / ((param['n_channel'] + 1) * 2)
        self.liquid_cell_W = (param['W_channel']/2)
          
        # elements = ((self.nx-1),(self.ny-1),(self.nz-1))
        elements2 = (self.nx+1,self.ny+1,self.nz+1) # padded by a zero on each side, note the offset hides a -1, -1 , -1 start index,
        # this makes looping much easier (see calculate_temperature in lmd_model.py)
            
        # Initialize Geometry - @colenockolds, please fill in the rest of the parameters and make sure they are consistent with the model
        # Cell-centered nodal arrays
        # example here https://github.com/hejob/taichi-fvm2d-fluid-ns/blob/master/multiblocksolver/block_solver.py
        self.temp = ti.field(ti.f32, shape = nodes,) 
        self.temp_next = ti.field(ti.f32, shape = nodes,)
        self.heat_flux = ti.field(ti.f32, shape = nodes,)
        self.isfluid = ti.field(ti.i32, shape = nodes,)

        self.volume = ti.field(ti.f32, shape = nodes,) # TODO @colenockolds
        self.interfaces = ti.field(ti.i32, shape = (*elements2,3), offset=(-1,-1,-1, 0)) # TODO  solid-solid has value 0, solid-fluid has value 1, fluid-fluid has value 2, @colenockolds
        self.interface_area = ti.field(ti.f32, shape = (*elements2,3), offset=(-1,-1,-1, 0)) # TODO area of interface between solid and fluid, @colenockolds

        # Volume of each cell designation
        self.volume_solid_cell_1 = self.cell_L * self.solid_cell_W * self.cell_H
        self.volume_liquid_cell = self.cell_L * self.liquid_cell_W * self.cell_H 
        self.volume_solid_cell_2 = self.volume_liquid_cell

        # x-axis interface areas between cells
        self.s1_s1_x_interface_area = self.cell_H * self.solid_cell_W
        self.l_l_x_interface_area = self.cell_H * self.liquid_cell_W
        self.s2_s2_x_interface_area = self.l_l_x_interface_area

        # y-axis interface area between cells
        self.y_interface_area = self.cell_L * self.cell_H

        # z-axis interface areas between cells
        self.s1_s1_z_interface_area = self.cell_L * self.solid_cell_W
        self.l_l_z_interface_area = self.cell_L * self.liquid_cell_W
        self.s2_s2_z_interface_area = self.l_l_z_interface_area

        def determine_volume(current_location):
            if current_location == 0:
            # We are at a fluid point
                V = self.volume_liquid_cell
            elif current_location == 1:
            # We are at a solid1 cell
                V = self.volume_solid_cell_1
            elif current_location == 2:
            # We are at a solid2 cell
                V = self.volume_solid_cell_2
            return V        
        
        def determine_interface_types(current_location, step_y, step_z):
            if current_location == 0:
            # We are at a fluid point
                Ix = 2
                if step_y == 0: Iy = 2
                else: Iy = 1
                if step_z == 0: Iz = 2
                else: Iz = 1
            elif current_location == 1:
            # We are at a solid1 cell
                Ix = 0
                Iz = 0
                if step_y == 0: Iy = 1
                else: Iy = 0
            elif current_location == 2:
            # We are at a solid2 cell
                Ix = 0
                Iy = 0
                if step_z == 0: Iz = 2
                else: step_z = 0
            return Ix, Iy, Iz
        
        def determine_interface_areas(current_location):
            Ay = self.y_interface_area
            if current_location == 0:
            # We are at a fluid point
                Ax = self.l_l_x_interface_area
                Az = self.l_l_z_interface_area
            elif current_location == 1:
            # We are at a solid1 cell
                Ax = self.s1_s1_x_interface_area
                Az = self.s1_s1_z_interface_area
            elif current_location == 2:
            # We are at a solid2 cell
                Ax = self.s2_s2_x_interface_area
                Az = self.s2_s2_z_interface_area
            return Ax, Ay, Az
        
        for i in range(self.nx):
            for j in range(self.nx):
                for k in range(self.nz):
                    point = self.isfluid[i,j,k]
                    self.volume[i,j,k] = determine_volume(point)
                    point_stepy = self.isfluid[i,j+1,k]
                    point_stepz = self.isfluid[i,j,k+1]
                    Ix, Iy, Iz = determine_interface_types(point, point_stepy, point_stepz)
                    self.interfaces[i,j,k,0] = Ix
                    self.interfaces[i,j,k,1] = Iy
                    self.interfaces[i,j,k,2] = Iz  
                    Ax, Ay, Az = determine_interface_areas(point)
                    self.interface_area[i,j,k,0] = Ax
                    self.interface_area[i,j,k,1] = Ay
                    self.interface_area[i,j,k,2] = Az

        self.heat_capacity = ti.field(ti.f32, shape = nodes,) # TODO @longvu
        
        # Resistance / intermediate arrays:
        self.current = ti.field(ti.f32, shape = (*elements2,self.nd), offset=(-1,-1,-1,0)) # 4D array (elements x nd), for x-y-z springs) (this is basically dynamic heat flux)
        self.heat_resist = ti.field(ti.f32, shape = (*elements2,self.nd), offset=(-1,-1,-1,0)) # 4D array (elements x nd), for x-y-z springs)
        
        # Fluid @akhilsadam
        self.pressure = ti.field(ti.f32, shape = nodes,) # from fluid
        self.velocity = ti.field(ti.f32, shape = (*nodes,self.nd)) # from fluid
        self.Re = ti.field(ti.f32, shape = nodes,) # from fluid
        self.Nu = ti.field(ti.f32, shape = nodes,) # from fluid
        
        self.A_channel = self.W_channel * self.H_channel # cross-sectional area [m^2]
        self.P_channel = 2 * (self.W_channel + self.H_channel) # perimeter [m]
        self.D_channel = 4 * self.A_channel / self.P_channel # hydraulic diameter [m]
            
            
        @ti.kernel
        def make_isfluid():
            for x in range(self.nx):
                for y in range(self.ny):
                    for z in range(self.nz):
                        if y % 4 > 1:
                            self.isfluid[x,y,1] = 0
                            self.isfluid[x,y,2] = 0
                            self.isfluid[x,y,0] = 2
                            self.isfluid[x,y,3] = 2
                        else: self.isfluid[x,y,z] = 1
        make_isfluid()
            
        @ti.func
        def channel_y(i:ti.i32, j:ti.i32, k:ti.i32):
            return 0.0 # TODO @colenockolds (want local coordinate in channel, with origin at center and normalized ranges [-1/2, 1/2])
        
        self.channel_y = channel_y
        
        @ti.func
        def channel_z(i:ti.i32, j:ti.i32, k:ti.i32):
            return 0.0 # TODO
        
        self.channel_z = channel_z
        
        @ti.func
        def ijk_to_xyz(i:ti.i32, j:ti.i32, k:ti.i32):
            x = i * self.cell_L
            z = k * self.cell_H
            if j % 4 == 3: 
                y = int(j/4) * 2 * (self.solid_cell_W + self.liquid_cell_W) + (2 * self.solid_cell_W + self.liquid_cell_W)
            else: 
                y = int(j/4) * 2 * (self.solid_cell_W + self.liquid_cell_W) + (j % 4) * self.solid_cell_W 
            return ti.Vector([x, y, z]) # TODO @colenockolds (want global position in meters; return ti.Vector or indexable tuple..not sure which works)

        self.ijk_to_xyz = ijk_to_xyz

    def ijk_to_xyz_host(self,i:ti.i32, j:ti.i32, k:ti.i32):
        x = i * self.cell_L
        z = k * self.cell_H
        if j % 4 == 3: 
            y = int(j/4) * 2 * (self.solid_cell_W + self.liquid_cell_W) + (2 * self.solid_cell_W + self.liquid_cell_W)
        else: 
            y = int(j/4) * 2 * (self.solid_cell_W + self.liquid_cell_W) + (j % 4) * self.solid_cell_W 
        return ti.Vector([x, y, z]) # TODO @colenockolds (want global position in meters; return ti.Vector or indexable tuple..not sure which works)


if __name__ == '__main__':
    from lmd_geometry import Geometry
    ti.init()
    g = Geometry()
    print('lmd_geometry.py succeeded!')