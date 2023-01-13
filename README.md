<!-- workflow badges -->
[![CodeQL](https://github.com/BYU-PRISM/Seeq/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/BYU-PRISM/Seeq/actions/workflows/codeql-analysis.yml)
[![Documentation](https://github.com/BYU-PRISM/Seeq/actions/workflows/pages/pages-build-deployment/badge.svg)](https://byu-prism.github.io/Seeq/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/BYU-PRISM/Seeq/binder?urlpath=apps%2Fsysid_notebook.ipynb)

<p align="left">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Title.png?raw=true" width="400" height="100"></p>

## System Identification
<!-- ![alt text](https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/digital_twin.svg?raw=true) -->
<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/digital_twin.svg?raw=true">
</p>

## Seeq-System Identification is ...
A Seeq Add-on built-in python to identify input and output relationships for the system to create **digital twin**
models for various analytics and machine learning tasks. System dynamics are identified thereby
allowing users to get dynamic predictions quickly. The Add-on is fully integrated with
Seeq Workbench. Cleaned and contextualized data from Seeq workbench can be used to identify dynamic models; the models can be pushed back into Seeq workbench. This framework supports both ad-hoc investigations as well as streaming predictions. The system identification framework can be used for a variety of tasks including simulation, digital twin construction, advanced process control, real-time optimization, etc.

<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Digital_twin_inout.png?raw=true" align="center" width="650" height="150">
</p>

## What does Seeq-System Identification do?
The System Identification Add-on supports the construction of a variety of dynamic models. White box models are primarily based on physics-based principles such as conservation laws and reaction kinetics for the chemical process. Development of these models requires extensive domain knowledge and is typically more expensive to build and maintain. Machine learning models are largely data-driven. Greybox models combine the best of both; they simplify the white-box model by lumping several parameters into fewer parameters that can be identified from data with higher degrees of confidence. These models are capable of capturing the primary dynamics of the system but are valid over smaller ranges of operation. The SysID Add-on allows users to choose a modeling option based on the application.


1. Grey-box model identification (ARX, Transfer Function, Subspace models)
1. Complex model identification (Neural Networks-based models)
1. Hybrid Physics and Machine learning model identification

<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Blackbox.png?raw=true" align="center" width="600" height="150">
</p>

## ARX model
ARX model is a system identification model that uses the linear correlation between previous and future values. ARX model consists of previous output terms (y) and previous input (u) terms multiplied by the linear coefficients (a, b). The linear combination of past input and output value computes the one-step-ahead prediction of output value(y<sub>k+1</sub>).
Multiple iterations of the one-step-ahead prediction return the multi-step prediction (from y<sub>k+1</sub> to y<sub>k+n</sub>). The time window of the past input and output terms is shifted toward the next segment for every iteration for multi-step prediction.
Here is an example formula with <img src="https://render.githubusercontent.com/render/math?math=\large n_a=3"> and <img src="https://render.githubusercontent.com/render/math?math=\large n_b=2"> for the single input and single output system,
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

Here is another example formula with **delay**  <img src="https://render.githubusercontent.com/render/math?math=\small (n_a=3, n_b=2, n_c=2)">,  

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large y_{k %2B 1}=a_{1} y_{k} %2B a_{2} y_{k-1} %2B a_{3} y_{k-2} %2B b_{1} u_{k-2-2} %2B b_{2} u_{k-1-2}" >
</p>

Although the ARX model can be more detailed by increasing the number of terms <img src="https://render.githubusercontent.com/render/math?math=\normalsize (n_a, n_b)">, it could result in an overfit. Thus, it could be an essential step to compare the training and validation set, ensuring the prediction for the validation set is as good as the training set. The model fitting can be quantified using different statistical methods such as **MSE** (Mean Squared Error) or **SSE** (Sum of Squared Error)


## Overview

<table border="0">
<td><img alt="image" src="https://github.com/BYU-PRISM/Seeq/blob/TF/docs/images/sysid-nn.png?raw=true"></td>
</table>

<a href="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-matrix-setup-sopdt.png">
<img alt="image" src="https://github.com/BYU-PRISM/Seeq/blob/TF/docs/images/sysid-matrix-setup-sopdt.png?raw=true" width=23%></a>
<!--  -->
<a href="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-tf-matrix2.png">
<img alt="image" src="https://github.com/BYU-PRISM/Seeq/blob/TF/docs/images/sysid-tf-matrix2.png?raw=true" width=23%></a>
<!--  -->
<a href="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-tf-setup.png">
<img alt="image" src="https://github.com/BYU-PRISM/Seeq/blob/TF/docs/images/sysid-tf-setup.png?raw=true" width=23%></a>
<!--  -->
<a href="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/seeq-sysid-gui.png">
<img alt="image" src="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/seeq-sysid-gui.png?raw=true" width=23%></a>
<!--  -->
<a href="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-ss.png">
<img alt="image" src="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-ss.png?raw=true" width=23%></a>
<!--  -->
<a href="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-matrix-loading.png">
<img alt="image" src="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-matrix-loading.png?raw=true" width=23%></a>
<!--  -->
<a href="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-step-info.png">
<img alt="image" src="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-step-info.png?raw=true" width=23%></a>
<!--  -->
<a href="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-arx.png">
<img alt="image" src="https://raw.githubusercontent.com/BYU-PRISM/Seeq/TF/docs/images/sysid-arx.png?raw=true" width=23%></a>
<br><br>
<!-- <p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/overview0.jpg?raw=true" align="center" width="800" height="602">
</p>
<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/overview1.png?raw=true" align="center" width="800" height="450">
</p>
<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/overview2.png?raw=true" align="center" width="800" height="450">
</p>
<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/overview3.png?raw=true" align="center" width="800" height="450">
</p> -->


# User Guide

https://user-images.githubusercontent.com/55245976/136423446-9babb1da-41e6-4fcc-8bc0-066f98fc189d.mp4

[**SeeQ-System Identification User Guide**](https://byu-prism.github.io/Seeq)
provides a more in-depth explanation of System Identification and how
seeq-sysid works.


# Installation

The backend of **seeq-sysid** requires **Python 3.7** or later.


## Dependencies

See [`requirements.txt`](https://github.com/BYU-PRISM/Seeq/blob/main/requirements.txt) file for a list of
dependencies and versions. Additionally, you will need to install the `seeq`
module with the appropriate version that matches your Seeq server. For more
information on the `seeq` module see
[seeq at pypi](https://pypi.org/project/seeq/).


## User Installation Requirements (Seeq Data Lab)

If you want to install **seeq-sysid** as a Seeq Add-on Tool, you will need:

- Seeq Data Lab (>= R52.1.5, >=R53.0.2, or >=R54)

- `seeq` module whose version matches the Seeq server version

- Seeq administrator access

- Enable Add-on Tools (or External Tools) in the Seeq server

*Note:* For older versions of Seeq Data Lab you can find the installation guide `here``](https://user-images.githubusercontent.com/55245976/137494969-43d93065-1e23-4e7c-952f-2397993eb269.mp4).
<!-- (>= R50.5.0, >=R51.1.0, or >=R52.1.0) -->


## User Installation (Seeq Data Lab)

1. Create a **new** Seeq Data Lab project and open the **Terminal** window
2. Run `pip install seeq-sysid`
3. Run `python -m seeq_sysid [--users <users_list> --groups <groups_list>]`

For more information about adding this addon to the seeq workbench
[click here](https://seeq.atlassian.net/wiki/spaces/KB/pages/961675391/Add-on+Tool+Administration+and+Development).


## Important links
* [Documentation for SysID Add-on](https://byu-prism.github.io/Seeq/)
* [Official source code repo](https://github.com/BYU-PRISM/Seeq)
* [System Identification with Industrial Data Webinar](https://youtu.be/glWIzPPJRnQ) 

<img align=left width=400px src='https://apmonitor.com/wiki/uploads/Main/2021_12_sysid.png'>
<br><br><br><br><br><br><br><br><br><br><br>


## Source code

You can get started by cloning the repository with the command:

```shell
git clone https://github.com/BYU-PRISM/Seeq.git
```

## Installation from source

For development work, it is highly recommended to create a python virtual
environment and install the package in that working environment.
If you are not familiar with python virtual environments, you can take a
look [here](https://docs.python.org/3.8/tutorial/venv.html)

Once your virtual environment is activated, you can install **seeq-sysid** from the source with:

Go to the setup.py directory (Seeq/'SysID Addon')
```shell
python setup.py install --user
```

*Note:* Remember that the `seeq` module version in your local environment should match the Seeq server version


### User Interface Testing

To test the UI, use the `developer_notebook.ipynb` in the root directory of this project.
This notebook can also be used while debugging from your IDE. You can also
create a whl first, install it on your virtual environment, and then
run `developer_notebook.ipynb` notebook there.


# Changelog

## v0.6.1
- Minor bugs fixed

## v0.6.0
- MA model added
- Units switch added
- Version number added to the GUI

## v0.5.1
- Minor bugs fixed

## v0.5.0

- ARIMAX model added
- Minor improvements
- GUI object moved to app.py
- Display results after calculation (Default)
- Unit compatibility error fixed
- Workbook pull step bypassed
- Push functions improved

## v0.4.1
- Hotfix for R57+ (search, pull, push functions)

## v0.4.0


- Export ARX model (Gekko sysid outputs as a pickle)
- Data Editor Added

## v0.3

- Push formula added for Transfer Function
- ARX Seeq formula fixed
- Mistune package conflict resolved

## v0.2

- Transfer Function
- Documentation added
- Shift method added to SubSpace.
- Installation made easier.
- Open Worksheet moved to the Hamburger Menu.

## v0.1

- Minor improvements

## v0.0.7

- Neural Network Model (RNN) added
- FIR Model added

## v0.0.6

- Installation made easier.

- N4SID method was removed temporarily.



# Support

Code related issues (e.g. bugs, feature requests) can be created in the
[issue tracker](https://github.com/BYU-PRISM/Seeq/issues)


# Citation

Please cite this work as:

```shell
seeq-sysid v0.6.1
BYU PRISM Group https://apm.byu.edu/prism/
https://github.com/BYU-PRISM/Seeq
```
