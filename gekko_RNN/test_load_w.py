from pickle import load

file = open(file='saved_weights.pkl', mode='rb')
# w0 = [W, Wh, b]
w0 = load(file)
file.close()

W = w0[0]
Wh = w0[1]
b = w0[2]
