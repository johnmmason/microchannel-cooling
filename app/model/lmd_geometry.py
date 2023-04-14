import taichi as ti    

@ti.data_oriented
class Geometry:
    def __init__(self, **kwargs):
        param = {
            'L_chip': 0.01464, 'W_chip': 0.0168, 'H_chip': 0.0001,
            'L_channel': 0.01464, 'W_channel': 500e-6, 'H_channel': 50e-6,
            'n_channel': 30,
            'nx': 100, 'ny': 100, 'nz': 3,
            'h': 1e-3, 'substep': 1,
            'dx': 1, 'dy': 1, 'dz': 1
        } | kwargs       
        
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
        self.dx = param['dx'] # finite difference step size (in space)
        self.dy = param['dy']
        self.dz = param['dz']
        self.nd = 3
        nodes = (self.nx,self.ny,self.nz)
          
        # elements = ((self.nx-1),(self.ny-1),(self.nz-1))
        elements2 = (self.nx+1,self.ny+1,self.nz+1) # padded by a zero on each side, note the offset hides a -1, -1 , -1 start index,
        # this makes looping much easier (see calculate_temperature in lmd_model.py)
            
        # Initialize Geometry - @colenockolds, please fill in the rest of the parameters and make sure they are consistent with the model
        # Cell-centered nodal arrays
        # example here https://github.com/hejob/taichi-fvm2d-fluid-ns/blob/master/multiblocksolver/block_solver.py
        self.temp = ti.field(ti.f32, shape = nodes,) 
        self.temp_next = ti.field(ti.f32, shape = nodes,)
        self.heat_flux = ti.field(ti.f32, shape = nodes,)
        self.isfluid = ti.field(ti.i32, shape = nodes,) # TODO @colenockolds
        self.volume = ti.field(ti.f32, shape = nodes,) # TODO @colenockolds
        self.heat_capacity = ti.field(ti.f32, shape = nodes,) # TODO @longvu
        
        # Resistance / intermediate arrays:
        self.current = ti.field(ti.f32, shape = (*elements2,self.nd), offset=(-1,-1,-1,0)) # 4D array (elements x nd), for x-y-z springs) (this is basically dynamic heat flux)
        self.heat_resist = ti.field(ti.f32, shape = (*elements2,self.nd), offset=(-1,-1,-1,0)) # 4D array (elements x nd), for x-y-z springs) 
        self.interfaces = ti.field(ti.i32, shape = elements2, offset=(-1,-1,-1)) # TODO  solid-solid has value 0, solid-fluid has value 1, fluid-fluid has value 2, @colenockolds
        self.interface_area = ti.field(ti.f32, shape = elements2, offset=(-1,-1,-1)) # TODO area of interface between solid and fluid, @colenockolds
        
        
        # Fluid @akhilsadam
        self.pressure = ti.field(ti.f32, shape = nodes,) # from fluid
        self.velocity = ti.field(ti.f32, shape = (*nodes,self.nd)) # from fluid
        self.Re = ti.field(ti.f32, shape = nodes,) # from fluid
        self.Nu = ti.field(ti.f32, shape = nodes,) # from fluid
        
        self.A_channel = self.W_channel * self.H_channel # cross-sectional area [m^2]
        self.P_channel = 2 * (self.W_channel + self.H_channel) # perimeter [m]
        self.D_channel = 4 * self.A_channel / self.P_channel # hydraulic diameter [m]
            
            
        @ti.func
        def channel_y(i:ti.i32, j:ti.i32, k:ti.i32):
            pass # TODO @colenockolds (want local coordinate in channel, with origin at center and normalized ranges [-1/2, 1/2])
        
        @ti.func
        def channel_z(i:ti.i32, j:ti.i32, k:ti.i32):
            pass # TODO
        
        @ti.func
        def ijk_to_xyz(i:ti.i32, j:ti.i32, k:ti.i32):
            x = (i / (self.nx - 1)) * self.L_chip
            y = (j / (self.ny - 1)) * self.W_chip
            z = (k / (self.ny - 1)) * self.W_chip
            return ti.Vector([x, y, z]) # TODO @colenockolds (want global position in meters; return ti.Vector or indexable tuple..not sure which works)

