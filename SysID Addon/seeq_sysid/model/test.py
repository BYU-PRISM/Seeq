from gekko import GEKKO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# load data
url = 'http://apmonitor.com/do/uploads/Main/tclab_siso_data.txt'
data = pd.read_csv(url)
t = data['time'].values
u = data['voltage'].values
y = data['temperature'].values

m = GEKKO(remote=False)
m.time = t; time = m.Var(0); m.Equation(time.dt()==1)

K = m.FV(lb=0,ub=1);      K.STATUS=1
tau = m.FV(lb=1,ub=300);  tau.STATUS=1
theta = m.FV(lb=2,ub=30); theta.STATUS=1

# create cubic spline with t versus u
uc = m.Var(u); tc = m.Var(t); m.Equation(tc==time-theta)
m.cspline(tc,uc,t,u,bound_x=False)

ym = m.Param(y)
yp = m.Var(y); m.Equation(tau*yp.dt()+(yp-y[0])==K*(uc-u[0]))

m.Minimize((yp-ym)**2)

m.options.IMODE=5
m.solve()

print('K: ', K.value[0])
print('tau: ',  tau.value[0])
print('theta: ', theta.value[0])

plt.figure()
plt.subplot(2,1,1)
plt.plot(t,u)
plt.legend([r'$V_1$ (mV)'])
plt.ylabel('MV Voltage (mV)')
plt.subplot(2,1,2)
plt.plot(t,y)
plt.plot(t,yp)
plt.legend([r'$T_{1meas}$',r'$T_{1pred}$'])
plt.ylabel('CV Temp (degF)')
plt.xlabel('Time')
plt.savefig('sysid.png')
plt.show()








