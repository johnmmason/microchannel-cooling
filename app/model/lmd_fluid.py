import taichi as ti


@ti.kernel
def calculate_Re(self):
    for i in range(self.geometry.nodes):
        self.geometry.Re[i] = self.fluid.rho * self.geometry.velocity[i] * self.geometry.D_channel / self.fluid.mu
 
@ti.kernel # TODO (@akhilsadam) improve to only calculate on edges!
def calculate_Nu(self):
    for i in range(self.geometry.nodes):
        Nu_uncor = 2 + 0.552 * self.geometry.Re[i]**0.5 * self.fluid.Pr**(1/3) # Nusselt number, uncorrected (Zhuifu, 2013)
        BTp = self.fluid.cp * (self.geometry.temp[i] - self.fluid.T_boiling_point) / self.fluid.latent_heat_of_vaporization # Spalding number (technically temp should be far-field, but this is for a vaporized droplet, so far-field is the same as local)
        fT = (1 + BTp)**(-2/3) # Zhuifu model (2013)
        self.geometry.Nu[i] = Nu_uncor*fT # Nusselt number, correction for Zhuifu model (2013

@ti.kernel
def setup_fluid(self):
    ql = self.Q / self.geometry.n_channel * 1e-6 / 60 # [m^3/s]
    v = ql / (self.geometry.W_channel * self.geometry.H_channel) 
    for i in range(self.geometry.nodes):
        # need a better reference:
        # https://www.researchgate.net/post/What-is-the-velocity-profile-of-laminar-flow-in-a-square-pipe
        y = self.geometry.channel_y(i)
        z = self.geometry.channel_z(i)
        vc = 32*v*y*(1-y)*z*(1-z) # TODO check this (@akhilsadam)
        self.geometry.velocity[i] = vc
        self.geometry.pressure[i] = 0.0 # TODO (@akhilsadam)