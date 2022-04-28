# What does Seeq-SysID do?

The System Identification Add-on supports contruction of a variety of dynamic models. White box models are primarily based on physics-based principles such as conservation laws and reaction kinetics for the chemical process. Development of these models requires extensive domain knowledge and is typically more expensive to build and maintain. Machine learning models are largely data driven. Greybox models combine the best of both; they simplify the white-box model by lumping several parameters into fewer parameters that can be identified from data with higher degrees of confidence. These models are capable of capturing the primary dynamics of the system but are valid over smaller ranges of operation. The SysID Add-on allows users to choose a modeling option based the application.


1. Grey-box model identification (ARX, Transferfunction, Subspace models)
2. Complex model identification (Neural Networks-based models)
3. Hybrid Physics and Machine learning model identification

<p align="center">
    <img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Blackbox.png?raw=true" align="center" width="600" height="150">
</p>
