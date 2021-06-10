import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import pandas as pd
from gekko import GEKKO

# load data and parse into columns
url = 'http://apmonitor.com/do/uploads/Main/cstr_step_tests.txt'
data = pd.read_csv(url)
print(data.head())

# generate time-series model
t = data['Time']
u = data['Tc']
y = data['T']
m = GEKKO(remote=True)

# system identification
na = 2 # output coefficients
nb = 2 # input coefficients
yp,p,K = m.sysid(t,u,y,na,nb,shift='init',scale=True,objf=100,diaglevel=1)

print(m.path)



# # plot results of fitting
# plt.figure()
# plt.subplot(2,1,1)
# plt.plot(t,u)
# plt.legend([r'$T_c$'])
# plt.ylabel('MV')
# plt.subplot(2,1,2)
# plt.plot(t,y)
# plt.plot(t,yp)
# plt.legend([r'$T_{meas}$',r'$T_{pred}$'])
# plt.ylabel('CV')
# plt.xlabel('Time')
# plt.savefig('sysid.png')
# plt.show()

# step test model
yc,uc = m.arx(p)

print(m.path)
print("Break")

# rename MV and CV
m.Tc = uc[0]
m.T = yc[0]

# steady state initialization
m.options.IMODE = 1
m.Tc.value = 280
m.solve(disp=True)

# GEKKO linear MPC
m.time = np.linspace(0,2,21)

# MV tuning
m.Tc.STATUS = 1
m.Tc.FSTATUS = 0
m.Tc.DMAX = 100
m.Tc.DCOST = 0.1
m.Tc.DMAXHI = 5   # constrain movement up
m.Tc.DMAXLO = -100 # quick action down
m.Tc.UPPER = 350
m.Tc.LOWER = 250
# CV tuning
m.T.STATUS = 1
m.T.FSTATUS = 1
m.T.SP = 330
m.T.TR_INIT = 1
m.T.TAU = 1.2
m.options.CV_TYPE = 2
m.options.IMODE = 6
m.options.SOLVER = 3

# define CSTR (plant)
def cstr(x,t,Tc):
    Ca,T = x
    Tf = 350; Caf = 1.0; q = 100; V = 100
    rho = 1000; Cp = 0.239; mdelH = 5e4
    EoverR = 8750; k0 = 7.2e10; UA = 5e4
    rA = k0*np.exp(-EoverR/T)*Ca
    dCadt = q/V*(Caf - Ca) - rA
    dTdt = q/V*(Tf - T) + mdelH/(rho*Cp)*rA + UA/V/rho/Cp*(Tc-T)
    return [dCadt,dTdt]

# Time Interval (min)
t = np.linspace(0,20,201)

# Store results for plotting
Ca_ss = 1; T_ss = 304; Tc_ss = 280
Ca = np.ones(len(t)) * Ca_ss
T = np.ones(len(t)) * T_ss
Tsp = np.ones(len(t)) * T_ss
Tc = np.ones(len(t)) * Tc_ss

# Set point steps
Tsp[0:40] = 330.0
Tsp[40:80] = 350.0
Tsp[80:120] = 370.0
Tsp[120:] = 390.0

# Create plot
plt.figure(figsize=(10,7))
plt.ion()
plt.show()

# Simulate CSTR
x0 = [Ca_ss,T_ss]
for i in range(len(t)-1):
    y = odeint(cstr,x0,[0,0.05],args=(Tc[i],))
    # retrieve measurements
    Ca[i+1] = y[-1][0]
    T[i+1] = y[-1][1]
    # insert measurement
    m.T.MEAS = T[i+1]
    # update setpoint
    m.T.SP = Tsp[i+1]
    # solve MPC
    m.solve(disp=True)
    # retrieve new Tc value
    Tc[i+1] = m.Tc.NEWVAL
    # update initial conditions
    x0[0] = Ca[i+1]
    x0[1] = T[i+1]

    #%% Plot the results
    plt.clf()
    plt.subplot(3,1,1)
    plt.plot(t[0:i],Tc[0:i],'b--',linewidth=3)
    plt.ylabel('Cooling T (K)')
    plt.legend(['Jacket Temperature'],loc='best')

    plt.subplot(3,1,2)
    plt.plot(t[0:i],Ca[0:i],'r-',linewidth=3)
    plt.ylabel('Ca (mol/L)')
    plt.legend(['Reactor Concentration'],loc='best')

    plt.subplot(3,1,3)
    plt.plot(t[0:i],Tsp[0:i],'k-',linewidth=3,label=r'$T_{sp}$')
    plt.plot(t[0:i],T[0:i],'b.-',linewidth=3,label=r'$T_{meas}$')
    plt.ylabel('T (K)')
    plt.xlabel('Time (min)')
    plt.legend(['Temperature SP','Reactor Temperature'],loc='best')
    plt.draw()
    plt.pause(0.01)