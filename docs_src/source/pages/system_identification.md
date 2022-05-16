# System Identification

System Identification is a set of methods to build a mathematical model based on the system’s input/output data.
\
One of the common techniques in identifying Time-Series is data-driven modeling. In this approach, The goal is to identify a reduced model that indicates mathematical relations between data without going into details. Different models can be used based on:

- System complexity

- Amount of available data

- Model application

- Quality of the data

Following sections will describe some of well-knowns models in this field.

## ARX model

ARX model is a system identification model that uses the linear correlation between previous and future values. ARX model consists of previous output terms (y) and previous input (u) terms multiplied by the linear coefficients (a, b). The linear combination of past input and output value computes the one-step-ahead prediction of output value(y<sub>k+1</sub>).
Multiple iterations of the one-step-ahead prediction return the multi-step prediction (from y<sub>k+1</sub> to y<sub>k+n</sub>). The time window of the past input and output terms is shifted toward next segment for every iteration for multi-step prediction.
Here is an example formular with <img src="https://render.githubusercontent.com/render/math?math=\large n_a=3"> and <img src="https://render.githubusercontent.com/render/math?math=\large n_b=2"> for the single input and single output system,
<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large y_{k %2B 1}=a_{0} y_{k} %2B a_{1} y_{k-1} %2B a_{2} y_{k-2} %2B b_{0} u_{k} %2B b_{1} u_{k-1}" >
</p>

<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Onestep-ahead.png?raw=true" align="center" width="300" height="100">
</p>

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

Which <img src="https://render.githubusercontent.com/render/math?math=\large x" > is the array of states, <img src="https://render.githubusercontent.com/render/math?math=\large u" > is the array of inputs, and <img src="https://render.githubusercontent.com/render/math?math=\large y" > is the array of outputs. <img src="https://render.githubusercontent.com/render/math?math=\large A" > is the transition matrix, <img src="https://render.githubusercontent.com/render/math?math=\large B"> is the input matrix, <img src="https://render.githubusercontent.com/render/math?math=\large C"> is the output matrix, and <img src="https://render.githubusercontent.com/render/math?math=\large D" > is the direct transition matrix or feedthrough matrix.
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

The first order plus deadtime is the simplest form of the transfer function. The structure and unit step response of a FOPDT has shown below.

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large \tau_p \frac{dy(t)}{dt} = -y(t)%2B K_p u(t-\theta_p) \ \Large \xrightarrow[\hspace{1cm}]\mathscr{L} \ \frac{y(s)}{u(s)} = \frac{K_p e^{-\theta s}}{\tau_p \ s %2B 1}" > 
</p>

## Neural Network model
