# Seeq

## ARX model
ARX model is a system identification model that uses the linear correlation between previous and future values. ARX model consists of previous output terms ($y$) and previous input ($u$) terms multiplied by the linear coefficients ($a$, $b$). The linear combination of past input and output value computes the one-step-ahead prediction of output value($y_{k+1}$). 
Multiple iterations of the one-step-ahead prediction return the multi-step prediction (from $y_{k+1}$ to $y_{k+n}$). The time window of the past input and output terms is shifted toward next segment for every iteration for multi-step prediction. 

Here is an example formular with $na=$3, $nb=$2 for the single input and single output system,

$y_{k+1}=a_{1} y_{k}+a_{2} y_{k-1}+a_{3} y_{k-2}+b_{1} u_{k}+b_{2} u_{k-1}$

ARX: Auto-Regressive with eXogenous input  
$a$: ARX coefficient for the past output value  
$b$: ARX coefficient for the past input value  
$na$: Number of terms for the past output value   
$nb$: Number of terms for the past input value  
$nk$: Delay between input and output  
$k$: present time step

Here is another example formular with **delay** ($na=$3, $nb=$2, $nk=$2),

$y_{k+1}=a_{1} y_{k}+a_{2} y_{k-1}+a_{3} y_{k-2}+b_{1} u_{k-2}+b_{2} u_{k-1-2}$

Although the ARX model can be more detailed by increasing the number of terms ($na$, $nb$), it could result in an overfit. Thus, it could be an essential step to compare the training and validation set, ensuring the prediction for the validation set is as good as the training set. The model fitting can be quantified using different statistical methods such as **MSE** (Mean Squared Error) or **SSE** (Sum of Squared Error)

