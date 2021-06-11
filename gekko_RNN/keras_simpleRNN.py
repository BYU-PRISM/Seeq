from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
import time

tf = 30 # fianl time

m=GEKKO(remote=False)
m.time = np.linspace(0,tf-1,tf)



K = m.FV(1) # Process Gain
tau = m.FV(2) # Time Constant

u_input = np.zeros(tf)
u_input[5:] = 1

y = m.CV()

u = m.MV(u_input)
m.Equation(tau*y.dt()+y==K*u) #FOPDT Equation

m.options.IMODE=4

m.solve(disp=False)

fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
fig.add_trace(go.Scatter(x=m.time, y=y.value,name="Output"), row=1, col=1,)
fig.add_trace(go.Scatter(x=m.time, y=u.value,name="Input"), row=2, col=1)
fig.update_layout(
    template="plotly_white",
    font_family="Times New Roman",
    font_size = 20
    )

fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, row=1 , col=1)
fig.update_xaxes(title_text='Time',showline=True, linewidth=2, linecolor='black', mirror=True, row=2, col=1)
fig.update_yaxes(title_text='y', showline=True, linewidth=2, linecolor='black', mirror=True, row=1, col=1)
fig.update_yaxes(title_text='u', showline=True, linewidth=2, linecolor='black', mirror=True, row=2, col=1)

# fig.show()


nstep = 400 # Choose training data lenth
x = np.linspace(0,nstep-1, nstep)

# random signal generation
np.random.seed(5) # seed to get constant result in each run
a_range = [0,2]
a = np.random.rand(nstep) * (a_range[1]-a_range[0]) + a_range[0] # range for amplitude
a[0] = 0

b_range = [5, 20]
b = np.random.rand(nstep) *(b_range[1]-b_range[0]) + b_range[0] # range for frequency
b = np.round(b)
b = b.astype(int)

b[0] = 0

for i in range(1,np.size(b)):
    b[i] = b[i-1]+b[i]

# Random Signal
i=0
random_signal = np.zeros(nstep)
while b[i]<np.size(random_signal):
    k = b[i]
    random_signal[k:] = a[i]
    i=i+1

# PRBS
a = np.zeros(nstep)
j = 0
while j < nstep:
    a[j] = 5
    a[j+1] = -5
    j = j+2

i=0
prbs = np.zeros(nstep)
while b[i]<np.size(prbs):
    k = b[i]
    prbs[k:] = a[i]
    i=i+1

fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
fig.add_trace(go.Scatter(y=random_signal,name="Output"), row=1, col=1,)
fig.add_trace(go.Scatter(y= prbs,name="Input"), row=2, col=1)
fig.update_layout(
    template="plotly_white",
    font_family="Times New Roman",
    font_size = 20
    )

fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, row=1 , col=1)
fig.update_xaxes(title_text='Time',showline=True, linewidth=2, linecolor='black', mirror=True, row=2, col=1)
fig.update_yaxes(title_text='y', showline=True, linewidth=2, linecolor='black', mirror=True, row=1, col=1)
fig.update_yaxes(title_text='u', showline=True, linewidth=2, linecolor='black', mirror=True, row=2, col=1)

# fig.show()

# """# 3. Evaluate the Random Input Signal"""

tf = nstep
m.time = np.linspace(0,tf-1,tf)
u.value = random_signal

m.options.IMODE = 4
m.solve(disp=False)

fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
fig.add_trace(go.Scatter(x=m.time, y=y.value,name="Output"), row=1, col=1,)
fig.add_trace(go.Scatter(x=m.time, y= u.value,name="Input"), row=2, col=1)
fig.update_layout(
    template="plotly_white",
    font_family="Times New Roman",
    font_size = 20
    )

fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, row=1 , col=1)
fig.update_xaxes(title_text='Time',showline=True, linewidth=2, linecolor='black', mirror=True, row=2, col=1)
fig.update_yaxes(title_text='y', showline=True, linewidth=2, linecolor='black', mirror=True, row=1, col=1)
fig.update_yaxes(title_text='u', showline=True, linewidth=2, linecolor='black', mirror=True, row=2, col=1)
# fig.show()


# """# 4. Train LSTM Network"""

from sklearn.preprocessing import MinMaxScaler
import joblib

# # For LSTM model
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import SimpleRNN
from keras.layers import Dropout
from keras.callbacks import EarlyStopping
from keras.models import load_model

window = 10 # window size for past value
P = 1 # Prediction Horizon for future prediction
#Load training data
data = pd.DataFrame(
        {"u": u,
         "y": y},
        index = np.linspace(1,nstep,nstep,dtype=int))

# Scale features
s1 = MinMaxScaler(feature_range=(-1,1))
Xs = s1.fit_transform(data[['u','y']])
s2 = MinMaxScaler(feature_range=(-1,1))
Ys = s2.fit_transform(data[['y']])

Ys = np.reshape(Ys, nstep)

fig = go.Figure()
fig.add_trace(go.Scatter(y=Ys,name="Ys"))
fig.add_trace(go.Scatter(y=Xs[:,1],name="Xs", line_dash='dash'))

fig.update_layout(
    template="plotly_white",
    font_family="Times New Roman",
    font_size = 20
    )
fig.update_xaxes(title_text='Time',showline=True, linewidth=2, linecolor='black', mirror=True)
fig.update_yaxes(title_text='y', showline=True, linewidth=2, linecolor='black', mirror=True)
# fig.show()

#%% Save MinMaxScaler file
joblib.dump(s1, 's1.sav')
joblib.dump(s2, 's2.sav')

val_ratio = 0.5 # or train ratio?
cut_index = np.int(nstep*val_ratio) # index number to separate the training and validation set
print(cut_index)
Xs_train = Xs[0:cut_index]
Ys_train = Ys[0:cut_index]
Xs_val = Xs[cut_index:]
Ys_val = Ys[cut_index:]

X_train = []
Y_train = []
for i in range(window,len(Xs_train)-P):
    X_train.append(Xs_train[i-window:i,:])
    Y_train.append([Ys_train[i]])

X_val = []
Y_val = []
for i in range(window,len(Xs_val)-P):
    X_val.append(Xs_val[i-window:i,:])
    Y_val.append([Ys_val[i]])

# """## (For Training) Preparing new LSTM Input data replacing the *y(k+1), .. y(k+P)* with *y(k)* """

# Reshape data to format accepted by LSTM
X_train, Y_train = np.array(X_train), np.array(Y_train)
X_val, Y_val = np.array(X_val), np.array(Y_val)

for i in range(0, len(X_train)):
  X_train[i][window:,1] = X_train[i][window-1,1]

for i in range(0, len(X_val)):
  X_val[i][window:,1] = X_val[i][window-1,1]

i = 30
t = np.linspace(0, 14, 15)
# plt.plot(t[5:],Y_train[i],'ro')
# plt.plot(t, X_train[i][:,1],'bo')
# plt.step(t, X_train[i][:,0])
# plt.show()

fig = go.Figure()
fig.add_trace(go.Scatter(x=t[5:],y=Y_train[i]))
fig.add_trace(go.Scatter(x=t, y=X_train[i][:,1], mode='markers'))
fig.add_trace(go.Scatter(x=t, y=X_train[i][:,0], line_shape='vh'))

fig.update_layout(
    template="plotly_white",
    font_family="Times New Roman",
    font_size = 20
    )
fig.update_xaxes(title_text='Time',showline=True, linewidth=2, linecolor='black', mirror=True)
fig.update_yaxes(title_text='y', showline=True, linewidth=2, linecolor='black', mirror=True)
# fig.show()

# # # Initialize LSTM model
model = Sequential()
# network structure: {2, 100, 1}
model.add(SimpleRNN(units=100, \
          input_shape=(X_train.shape[1],X_train.shape[2])))
model.add(Dropout(0.2))

# or ...
# network structure: {2, 100, 50, 1}
# model.add(SimpleRNN(units=100, \
#           input_shape=(X_train.shape[1],X_train.shape[2]), return_sequences=True))
# model.add(Dropout(0.2))
# model.add(SimpleRNN(units=50))
# model.add(Dropout(0.2))

model.add(Dense(units=Y_train.shape[1])) #units = number of outputs
model.compile(optimizer='adam', loss='mean_squared_error',\
              metrics=['accuracy'])
# Allow for early exit
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=10)

# Fit (and time) SimpleRNN model
t0 = time.time()
history = model.fit(X_train, Y_train, epochs=300, batch_size=32, callbacks=[es], verbose=1, validation_data=(X_val, Y_val))
t1 = time.time()
print('Runtime: %.2f s' %(t1-t0))

# Save Weights
from pickle import dump
W, Wh, b = [], [], []
for sub_w in model.weights:
    sub_type = (sub_w.name.split('/')[-1]).split(':')[0]
    if sub_type == 'kernel':  # Weights (W)
        W.append(sub_w.numpy())

    if sub_type == 'recurrent_kernel':  # Recurrent Weights (Wh)
        Wh.append(sub_w.numpy())

    if sub_type == 'bias':  # Biases (b)
        b.append(sub_w.numpy())

file = open(file='saved_weights.pkl',mode='wb')  # Saving variables
dump([W, Wh, b], file)
file.close()

# Save input/output data
file = open(file='saved_data.pkl',mode='wb')
dump([X_train, Y_train], file)
file.close()

# Save network model
model.save('SimpleRNN_model')

# Plot loss
plt.figure(figsize=(6,5))
plt.semilogy(history.history['loss'],label='train_loss')
plt.semilogy(history.history['val_loss'],label='val_loss')
plt.xlabel('epoch'); plt.ylabel('loss')
# plt.savefig('FOPDT_loss.png')
plt.legend()

# #%% Save model file
# if 'google.colab' in str(get_ipython()):
#   print('Running on Colab')
#   model.save('/content/drive/MyDrive/LSTM_MPC/FOPDT/model.h5')
    
# else:
#   print('Not running on Colab')
#   model.save('model.h5')

# """# 5. Prediction
# Input =    
# [x(k-W), x(k-w+1), ... x(k) ... x(k+P-1), x(k+P)],\
# [y(k-W), y(k-w+1), ... y(k) ... y(k+P-1), y(k+P)]
 
# where, y(k), ... y(k+p) : Same with the measured data

# Output = \
# [y(k) ... y(k+P-1), y(k+P)]
# """

# if 'google.colab' in str(get_ipython()):
#   print('Running on Colab')
#   model = load_model('/content/drive/MyDrive/LSTM_MPC/FOPDT/model.h5')
  
# else:
#   print('Not running on Colab')
#   model = load_model('model.h5')

# # Verify the fit of the model
t0 = time.time()
Yp_train = model.predict(X_train)
Yp_val = model.predict(X_val)
t1 = time.time()
print('Runtime: %.2f s' %(t1-t0))

# # un-scale outputs
Yu_train = s2.inverse_transform(Yp_train)
Ym_train = s2.inverse_transform(Y_train)

Yu_val = s2.inverse_transform(Yp_val)
Ym_val = s2.inverse_transform(Y_val)

plt.figure(0, figsize=(30,4))
plt.subplot(1,2,1)
plt.plot(data.index[window:cut_index-P],Yu_train[:,0],'r-',label='SimpleRNN')
plt.plot(data.index[window:cut_index-P],Ym_train[:,0],'b--',label='Measured')
plt.title('Training')
plt.legend()
plt.subplot(1,2,2)
plt.plot(data.index[cut_index+window:-P],Yu_val[:,0],'r-',label='SimpleRNN')
plt.plot(data.index[cut_index+window:-P],Ym_val[:,0],'b--',label='Measured')
plt.title('Validation')
plt.legend()
plt.show()




# plt.figure(0, figsize=(30,4))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train[:,0],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train[:,0],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val[:,0],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val[:,0],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()
# plt.show()

# plt.figure(1, figsize=(12,2))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train[:,1],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train[:,1],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val[:,1],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val[:,1],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()

# plt.figure(2, figsize=(12,2))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train[:,2],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train[:,2],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val[:,2],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val[:,2],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()

# plt.figure(3, figsize=(12,2))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train[:,3],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train[:,3],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val[:,3],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val[:,3],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()

# plt.figure(4, figsize=(12,2))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train[:,4],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train[:,4],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val[:,4],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val[:,4],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()

# j =206
# plt.subplot(2,1,1)
# plt.plot(Yu_val[j], 'r--', label='LSTM Prediction')

# plt.plot(Ym_val[j], label='Data')
# plt.subplot(2,1,2)
# plt.plot(X_val[j][window:,1], 'r-')
# plt.legend()

# """# 6. Forecast
# Input =  
# [x(k-W), x(k-w+1), ... x(k) ... x(k+P-1), x(k+P)],  
# [y(k-W), y(k-w+1), ... y(k) ... y(k+P-1), y(k+P)]

# where, [y(k+1), ... y(k+p)] = y(k) 

# Output =  
# [y(k) ... y(k+P-1), y(k+P)]
# """

# # Load model files (LSTM and MinMaxScaler)
# if 'google.colab' in str(get_ipython()):
#   print('Running on Colab')
#   model = load_model('/content/drive/MyDrive/LSTM_MPC/FOPDT/model.h5')
#   s1 = joblib.load('/content/drive/MyDrive/LSTM_MPC/FOPDT/s1.sav')
#   s2 = joblib.load('/content/drive/MyDrive/LSTM_MPC/FOPDT/s2.sav')
  
# else:
#   print('Not running on Colab')
#   model = load_model('model.h5')
#   s1 = joblib.load('s1.sav')
#   s2 = joblib.load('s2.sav')

# X_train_fcst = X_train.copy()
# X_val_fcst = X_val.copy()

# """## Preparing new LSTM Input data replacing the *y(k+1), .. y(k+P)* with *y(k)*"""

# for i in range(0, len(X_train_fcst)):
#   X_train_fcst[i][window:,1] = X_train_fcst[i][window-1,1]

# for i in range(0, len(X_val_fcst)):
#   X_val_fcst[i][window:,1] = X_val_fcst[i][window-1,1]

# X_train_fcst[350]

# # Verify the fit of the model
# t0 = time.time()
# Yp_train_fcst = model.predict(X_train_fcst)
# Yp_val_fcst = model.predict(X_val_fcst)
# t1 = time.time()
# print('Runtime: %.2f s' %(t1-t0))

# # un-scale outputs
# Yu_train_fcst = s2.inverse_transform(Yp_train_fcst)
# Ym_train_fcst = s2.inverse_transform(Y_train)

# Yu_val_fcst = s2.inverse_transform(Yp_val_fcst)
# Ym_val_fcst = s2.inverse_transform(Y_val)

# plt.figure(0, figsize=(30,4))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train_fcst[:,0],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train_fcst[:,0],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val_fcst[:,0],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val_fcst[:,0],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()

# plt.figure(1, figsize=(30,4))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train_fcst[:,1],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train_fcst[:,1],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val_fcst[:,1],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val_fcst[:,1],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()

# plt.figure(2, figsize=(30,4))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train_fcst[:,2],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train_fcst[:,2],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val_fcst[:,2],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val_fcst[:,2],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()

# plt.figure(3, figsize=(30,4))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train_fcst[:,3],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train_fcst[:,3],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val_fcst[:,3],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val_fcst[:,3],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()

# plt.figure(4, figsize=(30,4))
# plt.subplot(1,2,1)
# plt.plot(data.index[window:cut_index-P],Yu_train_fcst[:,4],'r-',label='LSTM')
# plt.plot(data.index[window:cut_index-P],Ym_train_fcst[:,4],'b--',label='Measured')
# plt.title('Training')
# plt.legend()
# plt.subplot(1,2,2)
# plt.plot(data.index[cut_index+window:-P],Yu_val_fcst[:,4],'r-',label='LSTM')
# plt.plot(data.index[cut_index+window:-P],Ym_val_fcst[:,4],'b--',label='Measured')
# plt.title('Validation')
# plt.legend()

# j = 206
# plt.subplot(2,1,1)
# plt.plot(Yu_val_fcst[j], 'r--', label='LSTM Prediction')

# plt.plot(Ym_val_fcst[j], label='Data')
# plt.subplot(2,1,2)
# plt.plot(X_val_fcst[j][window:,1], 'r-')
# plt.legend()

# """##Computation time for *P*-step ahead prediction"""

# X_in = X_train_fcst[140].reshape((1, window+P, np.shape(Xs)[1]))
# t0 = time.time()
# Y_out = model.predict(X_in)
# t1 = time.time()

# print(Y_out)
# print('Runtime for ' + str(P) +  ' step prediction: %.2f s' %(t1-t0))