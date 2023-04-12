import taichi as ti

@ti.kernel
def setup_fluid(self):
    ql = self.Q / self.geometry.n_channel * 1e-6 / 60 # [m^3/s]
    v = ql / (self.geometry.W_channel * self.geometry.H_channel) 
    for i in range(self.geometry.nx):
        for j in range(self.geometry.ny):
            for k in range(self.geometry.nz):
                # need a better reference:
                # https://www.researchgate.net/post/What-is-the-velocity-profile-of-laminar-flow-in-a-square-pipe
                y = self.geometry.channel_y(i, j, k)
                z = self.geometry.channel_z(i, j, k)
                vc = 32*v*y*(1-y)*z*(1-z) # TODO check this (@akhilsadam)
                self.geometry.velocity[i,j,k] = vc
                self.geometry.pressure[i,j,k] = 0.0 # TODO (@akhilsadam)