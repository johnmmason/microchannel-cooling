clear, clc, format long, clf, close all

c = 1; % counter
% Constants
L = 1e-1; % length of microchannel [m]
W = 100e-6; % width of microchannel [m]
for D = [10:1:50]*1e-6; % depth of microchannel [m]
A = W * D; % cross-sectional area [m^2] 
P = 2 * (W + D); % wetted perimeter [m]
Dh = 4 * A / P; % hydraulic diameter [m]

T_in = 20+273; % inlet temperature [K]
T_w = 100+273; % wall temperature [K]

rho = 997; % density of water [kg/m^3] % 961
mu = 0.00089; % viscosity of water [Pa*s] % 0.005
cp = 4180; % heat capacity of water [J/kg*K] % 1000
k = 0.606; % thermal conductivity of water [W/m*K] % 0.14

Q = [100]; % Flow rate in microliters per minute

% Fluid velocity
v = Q * 1.67e-11/ A;

% Reynolds number
Re = (rho * v * Dh) / mu;

% Prandtl number
Pr = cp * mu / k;

Nu = 0.023 * Re^(4/5) * Pr^(1/3);

% kandlikar model
% h = k / (2 * h) * (Re^0.8 * Pr^(1/3) / (1 + 12.7 * (Pr^(2/3) - 1) * (2 * h / w)^0.5));

% Heat transfer coefficienth
h = Nu * k / Dh; 

% Heat flux
q = h * (T_w - T_in);

% Pressure loss
f = 64 / Re; % friction factor for laminar flow in a smooth pipe
dP = (f * L * rho * v^2) / (2 * D);

% Outlet temperature
T_out = T_in + q / (rho * Q * cp);

% Display results
% fprintf("Heat flux: %.2f [W/cm^2]\n", q*1e-4);
% fprintf("Pressure loss: %.2f [psi]\n", dP*0.000145038);
% fprintf("Outlet temperature: %.2f [K]\n", T_out);

T(1,c) = D;
T(2,c) = q*1e-4;
T(3,c) = dP*0.000145038;
T(4,c) = Nu;
c = c+1;
end

figure(1)
subplot(1,2,1) % plot heat flux versus channel depth
semilogx(T(1,:),T(2,:),'-k','Linewidth', 1.5), hold on
xlabel('D (\mum)'), ylabel('Heat flux (W/cm^2)')
subplot(1,2,2) % plot pressre loss versus channel depth
semilogx(T(1,:),T(3,:),'-k','Linewidth', 1.5), hold on
xlabel('D (\mum)'), ylabel('\DeltaP (psi)')
