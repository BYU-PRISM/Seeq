import numpy as np
from pickle import load
import matplotlib.pyplot as plt
import keras


timesteps = 10  # time step
input_dim = 2  # input dimension
hidden_size = 100  # Size of hidden state or size of memory cell

inputs = np.random.random((timesteps, input_dim))  # 2D tensor (matrix)
print(inputs)

hidden_state_t = np.zeros(
    (hidden_size,))  # the first hidden state, 0 that goes into the first hidden layer along with the first input

print(hidden_state_t)  # Size of hidden state is 100, All 0 for the first hidden state value

# Wx = np.random.random((hidden_size, input_dim))  # 2D tensor for input weights, size in (100, 2)
# Wh = np.random.random((hidden_size, hidden_size)) # 2D tensor for hidden state weights, size in (100, 100)
# b = np.random.random((hidden_size,)) # 1D tensor for bias, size in (100,)
file = open(file='saved_data.pkl', mode='rb')
data = load(file)
file.close()
inputs = data[0]
outputs = data[1]

file = open(file='saved_weights.pkl', mode='rb')
w0 = load(file)
file.close()
Wx = w0[0]
Wh = w0[1]
b = w0[2]

print(np.shape(Wx))
print(np.shape(Wh))
print(np.shape(b))

total_hidden_states = []
total_outputs = []
output_t = []

# Memory cell
for input_t in inputs:  # input value at each input sequence
    hidden_state_t = np.zeros(hidden_size)  # Reset Hidden State after each sequence
    for t_s in input_t:
        # for layer in range(len())
        hideen_t = np.tanh(np.dot(t_s, Wx[0]) + np.dot(hidden_state_t, Wh[0]) + b[0])  # Wx * Xt + Wh * Ht-1 + b(bias)
        output_t = np.dot(hideen_t, Wx[1]) + b[1]
        total_hidden_states.append(list(hideen_t))  # append the hidden state at each time point
        # print(np.shape(total_hidden_states)) # output size of memory cell at each time step, (timestep, output_dim)
        hidden_state_t = hideen_t
    total_outputs.append(list(output_t))  # append the hidden state at each time point / Note: We only get last output
                                          # from each sequence and use other outputs to calculate hidden_state
                                          # We can also use all of that outputs to forecast outputs (Maybe!)

total_hidden_states = np.stack(total_hidden_states, axis=0)

# load keras SimpleRNN model
keras_RNN_model = keras.models.load_model('SimpleRNN_model')
# Calculate the keras_RNN outputs
keras_RNN_outputs = keras_RNN_model(inputs)

# Plot Results
plt.plot(total_outputs, '--k', label='Numpy_SimpleRNN', linewidth=2)
plt.plot(keras_RNN_outputs, ':r', label='keras_SimpleRNN', linewidth=2)
plt.plot(outputs, 'g', label='Measured', linewidth=2)

plt.legend()
plt.show()

