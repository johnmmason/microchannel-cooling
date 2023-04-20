import taichi as ti    

@ti.data_oriented
class Geometry:
    def __init__(self, **kwargs):  # sourcery skip: assign-if-exp
        # param = {
        #     'L_chip': 0.01464, 'W_chip': 0.0168, 'H_chip': 0.0001,
        #     'L_channel': 0.01464, 'W_channel': 500e-6, 'H_channel': 50e-6,
        #     'n_channel': 30,
        #     'nx': 100, 'ny_channel': 8, 'ny_wall': 1, 'nz_channel': 2, 'nz_wall': 1,
        #     'h': 1e-6, 'substep': 1,
        # } 
        param = {
            'L_chip': 0.02, 'W_chip': 0.00012, 'H_chip': 0.0001,
            'L_channel': 0.02, 'W_channel': 100e-6, 'H_channel': 50e-6,
            'n_channel': 1,
            'nx': 100, 'ny_channel': 8, 'ny_wall': 2, 'nz_channel': 8, 'nz_wall': 1,
            'h': 1e-6, 'substep': 1,
        } 
        param.update(kwargs)
        
        # for key, val in param.items():
        #     setattr(self, key, val)

        # real world measurements
        self.L_chip = param['L_chip']
        self.W_chip = param['W_chip']
        self.H_chip = param['H_chip']
        self.L_channel = param['L_channel']
        self.W_channel = param['W_channel']
        self.H_channel = param['H_channel']
        self.n_channel = param['n_channel']
               
        # problem setting
        self.nx = param['nx']
        self.ny = (param['ny_channel'] + param['ny_wall'] * 2) * (param['n_channel'])
        self.nz = (param['nz_channel'] + param['nz_wall'] * 2)

        # physical parameters
        # time-integration related
        self.h = param['h'] # time-step size
        self.substep = param['substep'] # number of substeps

        self.nd = 3
        nodes = (self.nx,self.ny,self.nz)
        # elements = ((self.nx-1),(self.ny-1),(self.nz-1))
        elements2 = (self.nx+1,self.ny+1,self.nz+1) # padded by a zero on each side, note the offset hides a -1, -1 , -1 start index,
        # this makes looping much easier (see calculate_temperature in lmd_model.py)
        
        @ti.kernel
        def zero_init(x: ti.template()):
            for i in ti.grouped(x):
                x[i] = 0.0

        self.cell_L = param['L_chip']/self.nx
        self.solid_cell_H = (param['H_chip'] -  param['H_channel']) / (2 * param['nz_wall'])
        self.liquid_cell_H = (param['H_channel']/param['nz_channel'])
        self.solid_cell_W = (param['W_chip'] - (param['n_channel'] * param['W_channel'])) / (param['n_channel'] * 2 * param['ny_wall'])
        self.liquid_cell_W = (param['W_channel']/param['ny_channel'])
        
        self.unit_width_real = self.W_chip / param['n_channel']
        self.unit_w_wall_real = self.solid_cell_W * param['ny_wall']
        self.unit_width =  (param['ny_channel'] + param['ny_wall'] * 2)
        self.unit_w_left = param['ny_wall']
        self.unit_w_right = param['ny_wall'] + param['ny_channel']
        self.unit_w_lr = param['ny_channel']
        
        self.unit_height_real = self.H_chip
        self.unit_h_wall_real = self.solid_cell_H * param['nz_wall']
        self.unit_height = (param['nz_channel'] + param['nz_wall'] * 2)
        self.unit_h_bottom = param['nz_wall']
        self.unit_h_top = param['nz_wall'] + param['nz_channel']
        self.unit_h_tb = param['nz_channel']
            
        # Initialize Geometry - @colenockolds, please fill in the rest of the parameters and make sure they are consistent with the model
        # Cell-centered nodal arrays
        # example here https://github.com/hejob/taichi-fvm2d-fluid-ns/blob/master/multiblocksolver/block_solver.py
        self.temp = ti.field(ti.f32, shape = nodes,) 
        self.temp_next = ti.field(ti.f32, shape = nodes,)
        self.heat_flux = ti.field(ti.f32, shape = nodes,)
        self.isfluid = ti.field(ti.i32, shape = nodes,)

        self.volume = ti.field(ti.f32, shape = nodes,) # TODO @colenockolds
        self.interfaces = ti.field(ti.i32, shape = (*elements2,self.nd), offset=(-1,-1,-1, 0)) # TODO  solid-solid has value 0, solid-fluid has value 1, fluid-fluid has value 2, @colenockolds
        self.interface_area = ti.field(ti.f32, shape = (*elements2,self.nd), offset=(-1,-1,-1, 0)) # TODO area of interface between solid and fluid, @colenockolds

        self.heat_capacity = ti.field(ti.f32, shape = nodes,) # TODO @longvu
        
        # Resistance / intermediate arrays:
        self.current = ti.field(ti.f32, shape = (*elements2,self.nd), offset=(-1,-1,-1,0)) # 4D array (elements x nd), for x-y-z springs) (this is basically dynamic heat flux)
        self.heat_resist = ti.field(ti.f32, shape = (*elements2,self.nd), offset=(-1,-1,-1,0)) # 4D array (elements x nd), for x-y-z springs)
        
        zero_init(self.heat_resist)
        zero_init(self.current)
        
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
                    y0 = y % self.unit_width
                    for z in range(self.nz):
                        if y0 >= self.unit_w_left and y0 < self.unit_w_right:
                            if z % self.unit_height >= self.unit_h_bottom and z % self.unit_height < self.unit_h_top:
                                self.isfluid[x,y,z] = 0 #fluid
                            else:
                                self.isfluid[x,y,z] = 3 #solid at bottom or top
                        elif z % self.unit_height >= self.unit_h_bottom and z % self.unit_height < self.unit_h_top:
                            self.isfluid[x,y,z] = 2
                        else:
                            self.isfluid[x,y,z] = 1
        make_isfluid()
        #-------------- # a side view (yz) of the chip (0 is a liquid cell, rest are solid cells)
        # | 1 | 3 | 1 |
        #--------------
        # | 2 | 0 | 2 |
        #--------------
        # | 1 | 3 | 1 |
        #--------------
        # Volume of each cell designation
        self.volume_solid_cell_1 = self.cell_L * self.solid_cell_W * self.solid_cell_H
        self.volume_solid_cell_2 = self.cell_L * self.solid_cell_W * self.liquid_cell_H
        self.volume_solid_cell_3 = self.cell_L * self.liquid_cell_W * self.solid_cell_H
        self.volume_liquid_cell = self.cell_L * self.liquid_cell_W * self.liquid_cell_H 
        
        # x-axis interface areas between cells
        self.s1_s1_x_interface_area = self.solid_cell_H * self.solid_cell_W
        self.l_l_x_interface_area = self.liquid_cell_H * self.liquid_cell_W
        self.s2_s2_x_interface_area = self.liquid_cell_H * self.solid_cell_W
        self.s3_s3_x_interface_area = self.solid_cell_H * self.liquid_cell_W

        # y-axis interface area between cells
        self.sy_interface_area = self.cell_L * self.solid_cell_H # same for 1,3
        self.ly_interface_area = self.cell_L * self.liquid_cell_H # same for 0,2

        # z-axis interface areas between cells
        self.sz_interface_area = self.cell_L * self.solid_cell_W # same for 1,2
        self.lz_interface_area = self.cell_L * self.liquid_cell_W # same for 0,3

        @ti.func
        def determine_volume(current_location):
            V = 0.0
            if current_location == 0:
            # We are at a fluid point
                V = self.volume_liquid_cell
            elif current_location == 1:
            # We are at a solid1 cell
                V = self.volume_solid_cell_1
            elif current_location == 2:
            # We are at a solid2 cell
                V = self.volume_solid_cell_2
            elif current_location == 3:
                V = self.volume_solid_cell_3
            return V        
        
        @ti.func
        def determine_interface_types(current_location, step_y, step_z):
            Ix = 0
            Iy = 0
            Iz = 0
            if current_location == 0:
            # We are at a fluid point
                Ix = 2
                if step_y == 0: Iy = 2 # 2 means liquid-liquid
                else: Iy = 1
                if step_z == 0: Iz = 2
                else: Iz = 1
            else:
            # We are at a solid cell
                Ix = 0
                if step_y == 0: Iy = 1 # 1 means solid-liquid
                else: Iy = 0 # 0 means solid-solid
                if step_z == 0: Iz = 1
                else: Iy = 0
            return Ix, Iy, Iz
        
        @ti.func
        def determine_interface_areas(current_location):
            Ax = 0.0
            Ay = 0.0
            Az = 0.0
            if current_location == 0:
            # We are at a fluid point
                Ax = self.l_l_x_interface_area
                Ay = self.ly_interface_area
                Az = self.lz_interface_area
            elif current_location == 1:
            # We are at a solid1 cell
                Ax = self.s1_s1_x_interface_area
                Ay = self.sy_interface_area
                Az = self.sz_interface_area
            elif current_location == 2:
            # We are at a solid2 cell
                Ax = self.s2_s2_x_interface_area
                Ay = self.ly_interface_area
                Az = self.sz_interface_area
            elif current_location == 3:
            # We are at a solid3 cell
                Ax = self.s3_s3_x_interface_area
                Ay = self.sy_interface_area
                Az = self.lz_interface_area
            return Ax, Ay, Az
        
        @ti.kernel
        def make_materials():
            # for i0 in range(self.nx+1):
            #     for j0 in range(self.ny+1):
                    i0 = 0
                    j0 = 0
                    for k0 in range(self.nz+1):
                        point = 0
                        i, j, k = i0, j0, k0 
                        if i0 < self.nx and j0 < self.ny and k0 < self.nz:      
                            point = self.isfluid[i,j,k]
                            self.volume[i,j,k] = determine_volume(point)
                        
                        if i0 >= self.nx:
                            i = i0 - 1
                        if j0 >= self.ny - 1:
                            j = 0
                        if k0 >= self.nz - 1:
                            k = 0
                        point = self.isfluid[i,j,k]
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
                        
                        print(point, self.interface_area[i,j,k,0]*1.0e11, self.interface_area[i,j,k,1]*1.0e11, self.interface_area[i,j,k,2]*1.0e11)

        # @ti.kernel
        # def adjust_materials():
            # for i in range(-1,self.nx + 1):
            #     for j in range(-1,self.ny + 1):
            #         for w in range(self.nd):
            #             self.interfaces[i,j,self.nz-1,w] = self.interfaces[i,j,0,w]
            #             self.interface_area[i,j,self.nz-1,w] = self.interface_area[i,j,0,w]
            #             self.interfaces[i,j,-1, w] = self.interfaces[i,j,0,w]
            #             self.interface_area[i,j,-1, w] = self.interface_area[i,j,0,w]


            # # repeat the above i,j loops for all 3 paired surfaces of the box in a loop
            # for k in range(-1,self.nz + 1):
            #     for j in range(-1,self.ny + 1):
            #         for w in range(self.nd):
            #             self.interfaces[self.nx,j,k,w] = 0
            #             self.interface_area[self.nx,j,k,w] = 0
                        
            # for i in range(-1,self.nx + 1):
            #     for k in range(-1,self.nz + 1):
            #         for w in range(self.nd):
            #             self.interfaces[i,self.ny,k,w] = self.interfaces[i,0,k,w]
            #             self.interface_area[i,self.ny,k,w] = self.interface_area[i,0,k,w]
            #             self.interfaces[i,-1,k, w] = self.interfaces[i,0,k,w]
            #             self.interface_area[i,-1,k, w] = self.interface_area[i,0,k,w]

                        
        make_materials()
        # adjust_materials()
        
        @ti.func
        def ijk_to_xyz(i:ti.i32, j:ti.i32, k:ti.i32): # TODO consolidate ifs to min/max or vice versa
            x = i * self.cell_L
        
            j0 = j % self.unit_width
            nj = int(j / self.unit_width)
            k0 = k % self.unit_height
            
            yshift = 0.0
            if j0 < self.unit_w_left:
                yshift = 0.5*self.solid_cell_W
            elif j0 < self.unit_w_right:
                yshift = 0.5*self.liquid_cell_W
            else:
                yshift = 0.5*self.solid_cell_W
            
            zshift = 0.0
            if k0 < self.unit_h_bottom:
                zshift = 0.5*self.solid_cell_H
            elif k0 < self.unit_h_top:
                zshift = 0.5*self.liquid_cell_H
            else:
                zshift = 0.5*self.solid_cell_H
            
            y = nj * self.unit_width_real \
                + ti.min(j0,self.unit_w_left)*self.solid_cell_W \
                + ti.min(ti.max(j0-self.unit_w_left,0),self.unit_w_lr)*self.liquid_cell_W \
                + ti.max(j0-self.unit_w_right,0)*self.solid_cell_W \
                + yshift    
                
            z = ti.min(k0,self.unit_h_bottom)*self.solid_cell_H \
                + ti.min(ti.max(k0-self.unit_h_bottom,0),self.unit_h_tb)*self.liquid_cell_H \
                + ti.max(k0-self.unit_h_top,0)*self.solid_cell_H \
                + zshift
                
            return x, y, z
                

        self.ijk_to_xyz = ijk_to_xyz

        @ti.func
        def channel_x_y_z(i,j,k):           
            rx, ry, rz = ijk_to_xyz(i,j,k)
            x = rx / self.L_channel
            z = ((rz - self.unit_h_wall_real) / self.H_channel) - 0.5
            ry = ry % self.unit_width_real
            y = ((ry - self.unit_w_wall_real) / self.W_channel) - 0.5
            return x, y, z
        
        self.channel_x_y_z = channel_x_y_z
        
    def ijk_to_xyz_host(self,i, j, k):
        x = i * self.cell_L
    
        j0 = j % self.unit_width
        nj = int(j / self.unit_width)
        k0 = k % self.unit_height
        
        y = nj * self.unit_width_real + min(j0,self.unit_w_left)*self.solid_cell_W + min(max(j0-self.unit_w_left,0),self.unit_w_lr)*self.liquid_cell_W + max(j0-self.unit_w_right,0)*self.solid_cell_W
        z = min(k0,self.unit_h_bottom)*self.solid_cell_H + min(max(k0-self.unit_h_bottom,0),self.unit_h_tb)*self.liquid_cell_H + max(k0-self.unit_h_top,0)*self.solid_cell_H
        return x, y, z

if __name__ == '__main__':
    from lmd_geometry import Geometry
    ti.init()
    g = Geometry()
    print('lmd_geometry.py succeeded!')