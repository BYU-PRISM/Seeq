# Seeq

## ARX model

ARX model is a system identification model that uses the linear correlation between previous and future values. ARX model consists of previous output terms ( 𝑦 ) and previous input ( 𝑢 ) terms multiplied by the linear coefficients ( 𝑎 ,  𝑏 ). The linear combination of past input and output value computes the one-step-ahead prediction of output value( 𝑦𝑘+1 ). Multiple iterations of the one-step-ahead prediction return the multi-step prediction (from  𝑦𝑘+1  to  𝑦𝑘+𝑛 ). The time window of the past input and output terms is shifted toward next segment for every iteration for multi-step prediction.

Here is an example formular with  𝑛𝑎= 3,  𝑛𝑏= 2 for the single input and single output system,

𝑦𝑘+1=𝑎1𝑦𝑘+𝑎2𝑦𝑘−1+𝑎3𝑦𝑘−2+𝑏1𝑢𝑘+𝑏2𝑢𝑘−1 
ARX: Auto-Regressive with eXogenous input
𝑎 : ARX coefficient for the past output value
𝑏 : ARX coefficient for the past input value
𝑛𝑎 : Number of terms for the past output value
𝑛𝑏 : Number of terms for the past input value
𝑛𝑘 : Delay between input and output
𝑘 : present time step

Here is another example formular with delay ( 𝑛𝑎= 3,  𝑛𝑏= 2,  𝑛𝑘= 2),

𝑦𝑘+1=𝑎1𝑦𝑘+𝑎2𝑦𝑘−1+𝑎3𝑦𝑘−2+𝑏1𝑢𝑘−2+𝑏2𝑢𝑘−1−2 
Although the ARX model can be more detailed by increasing the number of terms ( 𝑛𝑎 ,  𝑛𝑏 ), it could result in an overfit. Thus, it could be an essential step to compare the training and validation set, ensuring the prediction for the validation set is as good as the training set. The model fitting can be quantified using different statistical methods such as MSE (Mean Squared Error) or SSE (Sum of Squared Error)
