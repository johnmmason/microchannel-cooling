import taichi as ti    

class Geometry:
    def __init__(self, **kwargs):
        param = {
            'L_chip': 0.01464,
            'W_chip': 0.0168,
            'H_chip': 0.0001,
            'L_channel': 0.01464,
            'W_channel': 500e-6,
            'H_channel': 50e-6,
            'n_channel': 30,
            'nx': 100, # please fill in the rest of the parameters @colenockolds
        } | kwargs
               
        
        for key, val in param.items():
            setattr(self, key, val)
               
        # problem setting
        self.nx = nx
        self.ny = ny
        self.nz = nz

        # physical parameters
        # time-integration related
        self.h = h # time-step size
        self.substep = substep # number of substeps
        self.dx = dx # finite difference step size (in space)
        self.dy = dy
        self.dz = dz
        self.nd = 3
        nodes = self.nx * self.ny * self.nz   
        elements = (self.nx-1) * (self.ny-1) * (self.nz-1)
            
        # Initialize Geometry - @colenockolds, please fill in the rest of the parameters and make sure they are consistent with the model
        # Cell-centered nodal arrays
        # example here https://github.com/hejob/taichi-fvm2d-fluid-ns/blob/master/multiblocksolver/block_solver.py
        self.temp = ti.field(ti.f32, shape = nodes,) # unrolled to 1-d array
        self.temp_next = ti.field(ti.f32, shape = nodes,) # unrolled to 1-d array
        self.heat_flux = ti.field(ti.f32, shape = nodes,) # unrolled to 1-d array
        self.update = ti.field(ti.f32, shape = nodes,)
        self.isfluid = ti.field(ti.i32, shape = nodes,) # TODO @colenockolds
        
        # Resistance / intermediate arrays:
        self.heat_resist = ti.field(ti.f32, shape = (elements,self.nd),) # unrolled to 2D array (elements x nd), for x-y-z springs) 
        self.interfaces = ti.field(ti.i32, shape = elements,) # TODO unrolled to 1-d array, solid-solid has value 0, solid-fluid has value 1, fluid-fluid has value 2, @colenockolds
        self.interfaceArea = ti.field(ti.f32, shape = elements,) # TODO unrolled to 1-d array, area of interface between solid and fluid, @colenockolds
        
        
        # Fluid @akhilsadam
        self.pressure = ti.field(ti.f32, shape = nodes,) # from fluid
        self.velocity = ti.field(ti.f32, shape = nodes,) # from fluid
        self.Re = ti.field(ti.f32, shape = nodes,) # from fluid
        self.Nu = ti.field(ti.f32, shape = nodes,) # from fluid
        
        self.A_channel = self.W_channel * self.H_channel # cross-sectional area [m^2]
        self.P_channel = 2 * (self.W_channel + self.H_channel) # perimeter [m]
        self.D_channel = 4 * self.A_channel / self.P_channel # hydraulic diameter [m]
            
            
        @ti.func
        def channel_y(i:ti.i32): # note i is the unrolled index (so it's a 1D array instead of a 3D array)
            pass # TODO @colenockolds (want local coordinate in channel, with origin at center and normalized ranges [-1/2, 1/2])
        
        @ti.func
        def channel_z(i:ti.i32):
            pass # TODO
        
        @ti.func
        def i_to_xyz(i:ti.i32):
            pass # TODO @colenockolds (want global position in meters; return ti.Vector or indexable tuple..not sure which works)