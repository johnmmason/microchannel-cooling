import taichi as ti


@ti.kernel
def calculate_Re(fluid: ti.template(), geometry: ti.template()):
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
                geometry.Re[i,j,k] = fluid.rho * geometry.velocity[i,j,k,0] * geometry.D_channel / fluid.mu
 
@ti.kernel # TODO (@akhilsadam) improve to only calculate on edges!
def calculate_Nu(fluid: ti.template(), geometry: ti.template()):
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
                Nu_uncor = 2 + 0.552 * geometry.Re[i,j,k]**0.5 * fluid.Pr**(1/3) # Nusselt number, uncorrected (Zhuifu, 2013)
                BTp = fluid.cp * (geometry.temp[i,j,k] - fluid.T_boiling_point) / fluid.latent_heat_of_vaporization # Spalding number (technically temp should be far-field, but this is for a vaporized droplet, so far-field is the same as local)
                fT = (1 + BTp)**(-2/3) # Zhuifu model (2013)
                geometry.Nu[i,j,k] = Nu_uncor*fT # Nusselt number, correction for Zhuifu model (2013

@ti.kernel
def setup_fluid_velocity(Q: ti.f32, geometry: ti.template()):
    ql = Q / geometry.n_channel * 1e-6 / 60 # [m^3/s]
    v = ql / (geometry.W_channel * geometry.H_channel) 
    for i in range(geometry.nx):
        for j in range(geometry.ny):
            for k in range(geometry.nz):
                # need a better reference:
                # https://www.researchgate.net/post/What-is-the-velocity-profile-of-laminar-flow-in-a-square-pipe
                if geometry.isfluid[i,j,k] == 0:
                    _,y,z = geometry.channel_x_y_z(i,j,k)
                    vc = 32*v*y*(1-y)*z*(1-z) # TODO check this (@akhilsadam)
                    geometry.velocity[i,j,k,0] = vc
                else:
                    geometry.velocity[i,j,k,0] = 0.0
                geometry.velocity[i,j,k,1] = 0.0
                geometry.velocity[i,j,k,2] = 0.0
                geometry.pressure[i,j,k] = 0.0 # TODO (@akhilsadam)