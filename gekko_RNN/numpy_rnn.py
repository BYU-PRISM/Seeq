import numpy as np

timesteps = 10 # time step, length of sentence in NLP
input_dim = 4 # input dimension, work vector length in NLP
hidden_size = 8 # Size of hidden state, size of memory cell

inputs = np.random.random((timesteps, input_dim)) # 2D tensor (matrix)

hidden_state_t = np.zeros((hidden_size,)) # the first hidden state, 0 that goes into the first hidden layer along with the first input

print(hidden_state_t) # Size of hidden state is 8, All 0 for the first hidden state value

Wx = np.random.random((hidden_size, input_dim))  # 2D tensor for input weights, size in (8, 4)
Wh = np.random.random((hidden_size, hidden_size)) # 2D tensor for hidden state weights, size in (8, 8)
b = np.random.random((hidden_size,)) # 1D tensor for bias, size in (8,) 

print(np.shape(Wx))
print(np.shape(Wh))
print(np.shape(b))

total_hidden_states = []

# Memory cell
for input_t in inputs: # input value at each input sequence
  output_t = np.tanh(np.dot(Wx,input_t) + np.dot(Wh,hidden_state_t) + b) # Wx * Xt + Wh * Ht-1 + b(bias)
  total_hidden_states.append(list(output_t)) # append the hidden state at each time point
  print(np.shape(total_hidden_states)) # output size of memory cell at each time step, (timestep, output_dim)
  hidden_state_t = output_t

total_hidden_states = np.stack(total_hidden_states, axis = 0)
# re-organizing the result

print(total_hidden_states) # print out the all hidden state (timesteps, output_dim) (10, 8)