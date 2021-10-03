# Seeq

## ARX model
ARX model is a system identification model that uses the linear correlation between previous and future values. ARX model consists of previous output terms (y) and previous input (u) terms multiplied by the linear coefficients (a, b). The linear combination of past input and output value computes the one-step-ahead prediction of output value(y<sub>k+1</sub>). 
Multiple iterations of the one-step-ahead prediction return the multi-step prediction (from y<sub>k+1</sub> to y<sub>k+n</sub>). The time window of the past input and output terms is shifted toward next segment for every iteration for multi-step prediction. 

Here is an example formular with <img src="https://render.githubusercontent.com/render/math?math=\large n_a=3"> and <img src="https://render.githubusercontent.com/render/math?math=\large n_b=2"> for the single input and single output system,

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large y_{k %2B 1}=a_{0} y_{k} %2B a_{1} y_{k-1} %2B a_{2} y_{k-2} %2B b_{0} u_{k} %2B b_{1} u_{k-1}" >
</p>

**y<sub>k+1</sub>=a<sub>0</sub> y<sub>k</sub>+a<sub>1</sub> y<sub>k-1</sub>+a<sub>2</sub> y<sub>k-2</sub>+b<sub>0</sub> u<sub>k</sub>+b<sub>1</sub> u<sub>k-1</sub>**


ARX: Auto-Regressive with eXogenous input  
a: ARX coefficient for the past output value  
b: ARX coefficient for the past input value  
<img src="https://render.githubusercontent.com/render/math?math=\large n_a">: Number of terms for the past output value   
$nb$: Number of terms for the past input value  
$nk$: Delay between input and output  
$k$: present time step

Here is another example formular with **delay** ($na=$3, $nb=$2, $nk=$2),

$y_{k+1}=a_{1} y_{k}+a_{2} y_{k-1}+a_{3} y_{k-2}+b_{1} u_{k-2}+b_{2} u_{k-1-2}$

Although the ARX model can be more detailed by increasing the number of terms ($na$, $nb$), it could result in an overfit. Thus, it could be an essential step to compare the training and validation set, ensuring the prediction for the validation set is as good as the training set. The model fitting can be quantified using different statistical methods such as **MSE** (Mean Squared Error) or **SSE** (Sum of Squared Error)

