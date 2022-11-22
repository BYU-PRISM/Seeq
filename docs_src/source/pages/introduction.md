# Introduction
Seeq System Identification (Seeq-SysID) is an add-on to create a model from available signals on the Seeq Workbench to predict the system behavior based on the input data. The prediction results can be pushed back to Seeq Workbench.

<table border="0">
<td><img alt="image" src="../_static/sysid-nn.png?raw=true"></td>
</table>

<a href="../_static/sysid-matrix-setup-sopdt.png">
<img alt="image" src="../_static/sysid-matrix-setup-sopdt.png?raw=true" width=23%></a>
<!--  -->
<a href="../_static/sysid-tf-matrix2.png">
<img alt="image" src="../_static/sysid-tf-matrix2.png?raw=true" width=23%></a>
<!--  -->
<a href="../_static/sysid-tf-setup.png">
<img alt="image" src="../_static/sysid-tf-setup.png?raw=true" width=23%></a>
<!--  -->
<a href="../_static/seeq-sysid-gui.png">
<img alt="image" src="../_static/seeq-sysid-gui.png?raw=true" width=23%></a>
<!--  -->
<a href="../_static/sysid-ss.png">
<img alt="image" src="../_static/sysid-ss.png?raw=true" width=23%></a>
<!--  -->
<a href="../_static/sysid-matrix-loading.png">
<img alt="image" src="../_static/sysid-matrix-loading.png?raw=true" width=23%></a>
<!--  -->
<a href="../_static/sysid-step-info.png">
<img alt="image" src="../_static/sysid-step-info.png?raw=true" width=23%></a>
<!--  -->
<a href="../_static/sysid-arx.png">
<img alt="image" src="../_static/sysid-arx.png?raw=true" width=23%></a>

<p><p><p>

## What does Seeq-SysID do?

The System Identification Add-on supports the construction of a variety of dynamic models. White box models are primarily based on physics-based principles such as conservation laws and reaction kinetics for the chemical process. Development of these models requires extensive domain knowledge and is typically more expensive to build and maintain. Machine learning models are largely data-driven. Greybox models combine the best of both; they simplify the white-box model by lumping several parameters into fewer parameters that can be identified from data with higher degrees of confidence. These models are capable of capturing the primary dynamics of the system but are valid over smaller ranges of operation. The SysID Add-on allows users to choose a modeling option based on the application.


1. Grey-box model identification (ARX, Transfer function, Subspace models)
2. Complex model identification (Neural Networks-based models)
3. Hybrid Physics and Machine learning model identification

<p align="center">
    <img src="../_static/Blackbox.png?raw=true" align="center" width="600" height="150">
</p>

