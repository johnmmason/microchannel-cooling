import taichi as ti


@ti.kernel
def calculate_Re(fluid, geometry):
    for i in range(geometry.nodes):
        geometry.Re[i] = fluid.rho * geometry.velocity[i] * geometry.D_channel / fluid.mu
 
@ti.kernel # TODO (@akhilsadam) improve to only calculate on edges!
def calculate_Nu(fluid, geometry):
    for i in range(geometry.nodes):
        Nu_uncor = 2 + 0.552 * geometry.Re[i]**0.5 * fluid.Pr**(1/3) # Nusselt number, uncorrected (Zhuifu, 2013)
        BTp = fluid.cp * (geometry.temp[i] - fluid.T_boiling_point) / fluid.latent_heat_of_vaporization # Spalding number (technically temp should be far-field, but this is for a vaporized droplet, so far-field is the same as local)
        fT = (1 + BTp)**(-2/3) # Zhuifu model (2013)
        geometry.Nu[i] = Nu_uncor*fT # Nusselt number, correction for Zhuifu model (2013

@ti.kernel
def setup_fluid_velocity(geometry):
    ql = geometry.Q / geometry.n_channel * 1e-6 / 60 # [m^3/s]
    v = ql / (geometry.W_channel * geometry.H_channel) 
    for i in range(geometry.nodes):
        # need a better reference:
        # https://www.researchgate.net/post/What-is-the-velocity-profile-of-laminar-flow-in-a-square-pipe
        y = geometry.channel_y(i)
        z = geometry.channel_z(i)
        vc = 32*v*y*(1-y)*z*(1-z) # TODO check this (@akhilsadam)
        geometry.velocity[i] = vc
        geometry.pressure[i] = 0.0 # TODO (@akhilsadam)