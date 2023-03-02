#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt

c = 1 # counter

L = 0.1 # length of microchannel [m]
W = 100 * 10**(-6) # width of microchannel [m]
D = np.arange(10, 50, 1) * 10**(-6) # depth of microchannel [m]
A = W * D # cross-sectional area [m^2]
P = 2 * (W + D) # wetted perimeter [m]
Dh = 4 * A / P # hydraulic diameter [m]

T_in = 20 + 273 # inlet temperature [K]
T_w = 100 + 273 # inlet temperature [K]

rho = 997 # density of water [kg/m^3]
mu = 0.00089 # viscosity of water [Pa*s]
cp = 4180 # heat capacity of water [J/kg*K]
k = 0.606 # thermal conductivity of water [W/m*K]

Q = 100 # flow rate [uL/min]

v = Q * 1.67 * 10**(-11) / A # fluid velocity

# Reynolds number
Re = (rho * v * Dh) / mu

# Prandtl number
Pr = cp * mu / k

Nu = 0.023 * Re**(4/5) * Pr**(1/3)

# Kandlikar Model
# h = k / (2*h) * (Re^0.8 * Pr^(1/3) / (1 + 12.7 * (Pr^(2/3) - 1) * (2 * h/w)^0.5))

# heat transfer coefficent
h = Nu * k / Dh;

# heat flux
q = h * (T_w - T_in);

# pressure loss
f = 64/Re
dP = (f * L * rho * (v**2) ) / ( 2 * D )

# outlet temperature
T_out = T_in + q / (rho * Q * cp)

# plot
fig, (ax1, ax2)  = plt.subplots(1, 2)

fig.set_figwidth(10)
fig.set_figheight(6)
fig.tight_layout(pad=4)

ax1.plot( D, q * 10**(-4) )
ax1.set_xlabel('D ($\mu m$)')
ax1.set_ylabel('Heat Flux ($W/cm^2$)')
ax1.set_xscale('log')

ax2.plot( D, dP * 0.000145038 )
ax2.set_xlabel('D ($\mu m$)')
ax2.set_ylabel('$\delta P$ (psi)')
ax2.set_xscale('log')

plt.show()
