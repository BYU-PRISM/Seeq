import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from gekko import GEKKO
import tclab
import time

# -------------------------------------
# connect to Arduino
# -------------------------------------
a = tclab.TCLab()

# -------------------------------------
# import data
# -------------------------------------
url = 'https://apmonitor.com/do/uploads/Main/tclab_ss_data3.txt'
data = pd.read_csv(url)

# -------------------------------------
# scale data
# -------------------------------------
s = MinMaxScaler(feature_range=(0,1))
sc_train = s.fit_transform(data)

# partition into inputs and outputs
xs = sc_train[:,0:2] # 2 heaters
ys = sc_train[:,2:4] # 2 temperatures

# -------------------------------------
# build neural network
# -------------------------------------
nin = 2  # inputs
n1 = 2   # hidden layer 1 (linear)
n2 = 2   # hidden layer 2 (nonlinear)
n3 = 2   # hidden layer 3 (linear)
nout = 2 # outputs

# Initialize gekko models
train = GEKKO() 
mpc   = GEKKO(remote=False)
model = [train,mpc]

for m in model:
    # use APOPT solver
    m.options.SOLVER = 1

    # input(s)
    if m==train:
        # parameter for training
        m.inpt = [m.Param() for i in range(nin)]
    else:
        # variable for MPC
        m.inpt = [m.Var() for i in range(nin)]        

    # layer 1 (linear)
    m.w1 = m.Array(m.FV, (nout,nin,n1))
    m.l1 = [[m.Intermediate(sum([m.w1[k,j,i]*m.inpt[j] \
            for j in range(nin)])) for i in range(n1)] \
            for k in range(nout)]

    # layer 2 (tanh)
    m.w2 = m.Array(m.FV, (nout,n1,n2))
    m.l2 = [[m.Intermediate(sum([m.tanh(m.w2[k,j,i]*m.l1[k][j]) \
            for j in range(n1)])) for i in range(n2)] \
            for k in range(nout)]

    # layer 3 (linear)
    m.w3 = m.Array(m.FV, (nout,n2,n3))
    m.l3 = [[m.Intermediate(sum([m.w3[k,j,i]*m.l2[k][j] \
            for j in range(n2)])) for i in range(n3)] \
            for k in range(nout)]

    # outputs
    m.outpt = [m.CV() for i in range(nout)]
    m.Equations([m.outpt[k]==sum([m.l3[k][i] for i in range(n3)]) \
                 for k in range(nout)])

    # flatten matrices
    m.w1 = m.w1.flatten()
    m.w2 = m.w2.flatten()
    m.w3 = m.w3.flatten()

# -------------------------------------
# fit parameter weights
# -------------------------------------
m = train
for i in range(nin):
    m.inpt[i].value=xs[:,i]
for i in range(nout):
    m.outpt[i].value = ys[:,i]
    m.outpt[i].FSTATUS = 1
for i in range(len(m.w1)):
    m.w1[i].FSTATUS=1
    m.w1[i].STATUS=1
    m.w1[i].MEAS=1.0
for i in range(len(m.w2)):
    m.w2[i].STATUS=1
    m.w2[i].FSTATUS=1
    m.w2[i].MEAS=0.5
for i in range(len(m.w3)):
    m.w3[i].FSTATUS=1
    m.w3[i].STATUS=1
    m.w3[i].MEAS=1.0
m.options.IMODE = 2
m.options.EV_TYPE = 2

# solve for weights to minimize loss (objective)
m.solve(disp=True)

# -------------------------------------
# Create Model Predictive Controller
# -------------------------------------
m = mpc

# 60 second time horizon, steps of 3 sec
m.time = np.linspace(0,60,21)

# load neural network parameters
for i in range(len(m.w1)):
    m.w1[i].MEAS=train.w1[i].NEWVAL
    m.w1[i].FSTATUS = 1
for i in range(len(m.w2)):
    m.w2[i].MEAS=train.w2[i].NEWVAL
    m.w2[i].FSTATUS = 1
for i in range(len(m.w3)):
    m.w3[i].MEAS=train.w3[i].NEWVAL
    m.w3[i].FSTATUS = 1

# MVs and CVs
Q1 = m.MV(value=0)
Q2 = m.MV(value=0)
TC1 = m.CV(value=a.T1)
TC2 = m.CV(value=a.T2)

# scaled inputs to neural network
m.Equation(m.inpt[0] == Q1 * s.scale_[0] + s.min_[0])
m.Equation(m.inpt[1] == Q2 * s.scale_[1] + s.min_[1])

# define Temperature output
Q0 = 0   # initial heater
T0 = 23  # ambient temperature
# scaled steady state ouput
T1_ss = m.Var(value=T0)
T2_ss = m.Var(value=T0)
m.Equation(T1_ss == (m.outpt[0]-s.min_[2])/s.scale_[2])
m.Equation(T2_ss == (m.outpt[1]-s.min_[3])/s.scale_[3])
# time constants
tauA = m.Param(value=80)
tauB = m.Param(value=20)
TH1 = m.Var(a.T1)
TH2 = m.Var(a.T2)
# additional model equation for dynamics
m.Equation(tauA*TH1.dt()==-TH1+T1_ss)
m.Equation(tauA*TH2.dt()==-TH2+T2_ss)
m.Equation(tauB*TC1.dt()==-TC1+TH1)
m.Equation(tauB*TC2.dt()==-TC2+TH2)

# Manipulated variable tuning
Q1.STATUS = 1  # use to control temperature
Q1.FSTATUS = 0 # no feedback measurement
Q1.LOWER = 0.0
Q1.UPPER = 100.0
Q1.DMAX = 40.0
Q1.COST = 0.0
Q1.DCOST = 0.0

Q2.STATUS = 1  # use to control temperature
Q2.FSTATUS = 0 # no feedback measurement
Q2.LOWER = 0.0
Q2.UPPER = 100.0
Q2.DMAX = 40.0
Q2.COST = 0.0
Q2.DCOST = 0.0

# Controlled variable tuning
TC1.STATUS = 1     # minimize error with setpoint range
TC1.FSTATUS = 1    # receive measurement
TC1.TR_INIT = 1    # reference trajectory
TC1.TAU = 10       # time constant for response

TC2.STATUS = 1     # minimize error with setpoint range
TC2.FSTATUS = 1    # receive measurement
TC2.TR_INIT = 1    # reference trajectory
TC2.TAU = 10       # time constant for response

# Global Options
m.options.IMODE   = 6 # MPC
m.options.CV_TYPE = 1 # Objective type
m.options.NODES   = 3 # Collocation nodes
m.options.SOLVER  = 3 # 1=APOPT, 3=IPOPT

# -------------------------------------
# Initialize model and data storage
# -------------------------------------

# Get Version
print(a.version)

# Turn LED on
print('LED On')
a.LED(100)

# Run time in minutes
run_time = 10.0

# Number of cycles with 3 second intervals
loops = int(20.0*run_time)
tm = np.zeros(loops)

# Temperature (K)
T1 = np.ones(loops) * a.T1 # temperature (degC)
T1sp = np.ones(loops) * 35.0 # set point (degC)
T2 = np.ones(loops) * a.T2 # temperature (degC)
T2sp = np.ones(loops) * 23.0 # set point (degC)

# Set point changes
T1sp[3:] = 40.0
T2sp[40:] = 30.0
T1sp[80:] = 32.0
T2sp[120:] = 35.0
T1sp[160:] = 45.0

# heater values
Q1s = np.ones(loops) * 0.0
Q2s = np.ones(loops) * 0.0

# Create plot
plt.figure()
plt.ion()
plt.show()

# Main Loop
start_time = time.time()
prev_time = start_time
try:
    for i in range(1,loops):
        # Sleep time
        sleep_max = 3.0
        sleep = sleep_max - (time.time() - prev_time)
        if sleep>=0.01:
            time.sleep(sleep)
        else:
            time.sleep(0.01)

        # Record time and change in time
        t = time.time()
        dt = t - prev_time
        prev_time = t
        tm[i] = t - start_time

        # Read temperatures in Kelvin 
        T1[i] = a.T1
        T2[i] = a.T2

        ###############################
        ### MPC CONTROLLER          ###
        ###############################
        TC1.MEAS = T1[i]
        TC2.MEAS = T2[i]
        # input setpoint with deadband +/- DT
        DT = 0.1
        TC1.SPHI = T1sp[i] + DT
        TC1.SPLO = T1sp[i] - DT
        TC2.SPHI = T2sp[i] + DT
        TC2.SPLO = T2sp[i] - DT
        # solve MPC
        m.solve(disp=False)    
        # test for successful solution
        if (m.options.APPSTATUS==1):
            # retrieve the first Q value
            Q1s[i] = Q1.NEWVAL
            Q2s[i] = Q2.NEWVAL
        else:
            # not successful, set heater to zero
            Q1s[i] = 0        
            Q2s[i] = 0        

        # Write output (0-100)
        a.Q1(Q1s[i])
        a.Q2(Q2s[i])

        # Plot
        plt.clf()
        ax=plt.subplot(3,1,1)
        ax.grid()
        plt.plot(tm[0:i],T1[0:i],'ro',MarkerSize=3,label=r'$T_1$')
        plt.plot(tm[0:i],T1sp[0:i],'k-',LineWidth=2,label=r'$T_1 SP$')
        plt.ylabel('Temperature (degC)')
        plt.legend(loc='best')
        ax=plt.subplot(3,1,2)
        ax.grid()
        plt.plot(tm[0:i],T2[0:i],'ro',MarkerSize=3,label=r'$T_2$')
        plt.plot(tm[0:i],T2sp[0:i],'g-',LineWidth=2,label=r'$T_2 SP$')
        plt.ylabel('Temperature (degC)')
        plt.legend(loc='best')
        ax=plt.subplot(3,1,3)
        ax.grid()
        plt.plot(tm[0:i],Q1s[0:i],'r-',LineWidth=3,label=r'$Q_1$')
        plt.plot(tm[0:i],Q2s[0:i],'b:',LineWidth=3,label=r'$Q_2$')
        plt.ylabel('Heaters')
        plt.xlabel('Time (sec)')
        plt.legend(loc='best')
        plt.draw()
        plt.pause(0.05)

    # Turn off heaters
    a.Q1(0)
    a.Q2(0)
    print('Shutting down') 

# Allow user to end loop with Ctrl-C           
except KeyboardInterrupt:
    # Disconnect from Arduino
    a.Q1(0)
    a.Q2(0)
    print('Shutting down')
    a.close()

# Make sure serial connection still closes when there's an error
except:           
    # Disconnect from Arduino
    a.Q1(0)
    a.Q2(0)
    print('Error: Shutting down')
    a.close()
    raise