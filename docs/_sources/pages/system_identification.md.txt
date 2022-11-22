# System Identification

System Identification is a set of methods to build a mathematical model based on the system’s input/output data.
\
One of the common techniques in identifying Time-Series is data-driven modeling. In this approach, The goal is to identify a reduced model that indicates mathematical relations between data without going into details. Different models can be used based on:

- System complexity

- Amount of available data

- Model application

- Quality of the data

The following sections will describe some of the well-known models in this field.

## ARX model

ARX model is a system identification model that uses the linear correlation between previous and future values. ARX model consists of previous output terms (y) and previous input (u) terms multiplied by the linear coefficients (a, b). The linear combination of past input and output value computes the one-step-ahead prediction of output value(y<sub>k+1</sub>).
Multiple iterations of the one-step-ahead prediction return the multi-step prediction (from y<sub>k+1</sub> to y<sub>k+n</sub>). The time window of the past input and output terms is shifted toward next segment for every iteration for multi-step prediction.
Here is an example formular with <img src="https://render.githubusercontent.com/render/math?math=\large n_a=3"> and <img src="https://render.githubusercontent.com/render/math?math=\large n_b=2"> for the single input and single output system,
<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large y_{k %2B 1}=a_{0} y_{k} %2B a_{1} y_{k-1} %2B a_{2} y_{k-2} %2B b_{0} u_{k} %2B b_{1} u_{k-1}" >
</p>

<!-- <p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Onestep-ahead.png?raw=true" align="center" width="300" height="100">
</p> -->

<img src="https://render.githubusercontent.com/render/math?math=\large ARX">: Auto-Regressive with eXogenous input
("Auto" indicates the past 'y' values, and "Exogenous" indicates the past 'u' values serving as model inputs)  
<img src="https://render.githubusercontent.com/render/math?math=\large a">: ARX coefficient for the past output value  
<img src="https://render.githubusercontent.com/render/math?math=\large b">: ARX coefficient for the past input value  
<img src="https://render.githubusercontent.com/render/math?math=\large n_a">: Number of terms for the past output value  
<img src="https://render.githubusercontent.com/render/math?math=\large n_b">: Number of terms for the past input value  
<img src="https://render.githubusercontent.com/render/math?math=\large n_c">: Delay between input and output  
<img src="https://render.githubusercontent.com/render/math?math=\large k">: present time step  

Here is another example formular with **delay**  <img src="https://render.githubusercontent.com/render/math?math=\small (n_a=3, n_b=2, n_c=2)">,  

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large y_{k %2B 1}=a_{1} y_{k} %2B a_{2} y_{k-1} %2B a_{3} y_{k-2} %2B b_{1} u_{k-2-2} %2B b_{2} u_{k-1-2}" >
</p>

Although the ARX model can be more detailed by increasing the number of terms <img src="https://render.githubusercontent.com/render/math?math=\normalsize (n_a, n_b)">, it could result in an overfit. Thus, it could be an essential step to compare the training and validation set, ensuring the prediction for the validation set is as good as the training set. The model fitting can be quantified using different statistical methods such as **MSE** (Mean Squared Error) or **SSE** (Sum of Squared Error). [Read more](https://apmonitor.com/wiki/index.php/Apps/ARXTimeSeries) about ARX models.

## State Space model

The [**State Space**](https://apmonitor.com/pdc/index.php/Main/StateSpaceModel) model is one of the linear representations of dynamic systems. Converting a model to a State Space structure is routine for process control and optimization applications. These models can be used for both continuous and discrete forms.

<table border="0" align="center">

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large \dot{x} = Ax %2B Bu" >
</p>

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large y = Cx %2B Du" >
</p>
 <tr>
    <td>Figure 2. Continuous State Space model structure.</td>
 </tr>
</table>
<br>

Which <img src="https://render.githubusercontent.com/render/math?math=\large x" > is the array of states, <img src="https://render.githubusercontent.com/render/math?math=\large u" > is the array of inputs, and <img src="https://render.githubusercontent.com/render/math?math=\large y" > is the array of outputs. <img src="https://render.githubusercontent.com/render/math?math=\large A" > is the transition matrix, <img src="https://render.githubusercontent.com/render/math?math=\large B"> is the input matrix, <img src="https://render.githubusercontent.com/render/math?math=\large C"> is the output matrix, and <img src="https://render.githubusercontent.com/render/math?math=\large D"> is the direct transition matrix or feedthrough matrix.
Considering **n** states, **m** inputs, and **p** outputs:

<table border="0" align="center">

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large A\in \mathbb{R}^{n \times n}" >
</p>

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large B\in \mathbb{R}^{n \times m}" >
</p>

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large C\in \mathbb{R}^{p \times n}" >
</p>

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large D\in \mathbb{R}^{p \times m}" >
</p>
</table>

that <img src="https://render.githubusercontent.com/render/math?math=\large \mathbb{R}" > indicates set of real numbers. [Read more](http://apmonitor.com/wiki/index.php/Apps/LinearStateSpace) about State Space models.

## Transfer Function

Transfer functions are the linearized representations of dynamic systems. The first step to create a transfer function is to calculate the Laplace transform of a differential equation. After applying Laplace transform differential equation converts to an algebraic equation. These algebraic equations can be transformed back into the time domain.

In the industry, transfer functions are base of many prediction and control tuning applications. 
For the sake of simplicity first, order and second-order transfer functions are more common than others:

### First Order Plus Deadtime (FOPDT)

The first order plus deadtime is the simplest form of the transfer function. The structure and unit step response of a FOPDT has shown below. in this equation <img src="https://render.githubusercontent.com/render/math?math=\large \tau_p"> is the process time constant, <img src="https://render.githubusercontent.com/render/math?math=\large K_p"> is the process gain, <img src="https://render.githubusercontent.com/render/math?math=\large \theta_p"> is the process deadtime, <img src="https://render.githubusercontent.com/render/math?math=\large y"> is the process output and <img src="https://render.githubusercontent.com/render/math?math=\large u"> is the process input.

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large \tau_p \frac{dy(t)}{dt} = -y(t)%2B K_p u(t-\theta_p) \ \Large \xrightarrow[\hspace{1cm}]\mathscr{L} \ \frac{y(s)}{u(s)} = \frac{K_p e^{-\theta s}}{\tau_p \ s %2B 1}" > 
</p>

<figure class="image" align="center">
   <img src="../_static/fopdt.png?raw=true" align="center">
   </p>
   <figcaption>Figure 1. FOPDT step response</figcaption>
</figure>

### Second Order Plus Deadtime (SOPDT)
The step response of SOPDT is usually S-shaped. In the SOPDT equation <img src="https://render.githubusercontent.com/render/math?math=\large \zeta"> is the relative damping factor. Overshoot, Settling time and Rise time are other characterestics of SOPDT step response.

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large \tau_p^2 \frac{d^2y}{dt^2} %2B 2 \tau_p \zeta \frac{dy(t)}{dt} = -y(t)%2B K_p u(t-\theta_p) \ \Large \xrightarrow[\hspace{1cm}]\mathscr{L} \ \frac{y(s)}{u(s)} = \frac{K_p e^{-\theta s}}{(\tau_p \ s)^2 %2B 2\tau_p\zeta %2B   1}" > 
</p>

<figure class="image" align="center">
<img src="../_static/sopdt.png?raw=true" align="center">
   </p>
   <figcaption>Figure 2. SOPDT step response</figcaption>
</figure>

## Neural Network model

Neural networks are a set of neurons contacting each other using corresponding weight coefficients. There are many kinds of neural networks, according to their application. Multilayer Perceptron is commonly used for control applications because of its simplicity and fast response. This neural network is made up of three sections: the input layer, the hidden layer(s), and the output layer. An input layer, where the input data comes in. It is conventional to normalize data before calculations to avoid neuron saturation. Neuron saturation is a state that which a neuron gives a constant value for each entering data. The output layer receives the output data and denormalizes the results. The layers between the input layer and the output layer call the hidden layer(s) where. The number of these layers and their neurons can vary depending on the complexity of the system. Increasing hidden layers and neurons require more data and time to train the network.

<figure class="image" align="center">
   <a href="../_static/FF3.svg">
   <img alt="simple_nn" src="../_static/FF3.svg?raw=true" width=90%></a>
   <figcaption>Figure 3. A simple neural network with one hidden layer</figcaption>
</figure>

Inputs of the network are input(s), delayed input(s), output(s), and delayed output(s) of the system. The number of delays given to the inputs and outputs of the system depends on its complexity. After specifying the network’s structure (number of hidden layers, number of neurons in each layer, inputs, and output of the network), weights and biases will be initialized randomly. Normalized data will be passed through the network, identification error will be calculated, the error backpropagates through the network, and weights and biases will be updated till the Mean of Square Error (MSE) meats the specified criteria then the training procedure will be terminated. Now the network is ready to mimic the system’s behavior and can be used as a model which correlates the input(s) and output(s) of the system.

<figure class="image" align="center">
   <a href="../_static/nnid-flow.jpg">
   <img alt="neuralnetwork_flowchart" src="../_static/nnid-flow.jpg" width=90%></a>
   </p>
   <figcaption>Figure 4. Neural network identification flowchart</figcaption>
</figure>