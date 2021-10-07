<p align="left">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Title.png" width="400" height="100"></p>

## System Identification
<!-- ![alt text](https://github.com/BYU-PRISM/Seeq/blob/main/SysID_Gui.png?raw=true) -->
<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/digital_twin.svg">
</p>

## SeeQ-System Identification is .. 
A Python module to identify input and output relationship for the system to create the **digital twin** 
models for various data analytics tasks. It provides various models to identify the system dynamics 
allowing users to get the model prediction value quickly. The Add-On module can be integrated into 
the Seeq Workbench and passing the data from the Workbench and Identified model results from the 
Add-on back and forth. It also provides the model result in a formula to predict the system behavior 
for the time range beyond the training data. The model result can be used for many different data 
analytics tasks, plus for the model development tasks for the Advanced Process Control applications.

<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Digital_twin_inout.png" align="center" width="650" height="150">
</p>

## What does Seeq-System Identification do?
Seeq-System Identification Add-on provides a spectrum of the prediction model ranging from Linear-time invariant (LTI) to the Machine learning model. The white box models are consist of physics-based principles such as conservation laws and reaction kinetics for the chemical process. However, the model development requires much domain knowledge; thus, the engineering cost can be higher than data-driven models. On the other hand, the black-box models, such as Machine Learning models, are entirely driven by the data, but they require a lot of data to acquire the usable model. Greybox models are a simplified version of the white-box model by lumping several parameters into a single property. They can capture the main dynamics of the system well, but they usually can cover the relatively narrow operation range because of the linearity of the model. Seeq users can have various options of model for the specific problems from the Seeq SysID app.


1. Grey-box model identification (ARX, Transferfunction, Subspace models)
1. Black-box model identification (Neural Networks-based models)
1. Hybrid Physics and Machine learning model identification

<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Blackbox.png" align="center" width="600" height="150">
</p>

## ARX model
ARX model is a system identification model that uses the linear correlation between previous and future values. ARX model consists of previous output terms (y) and previous input (u) terms multiplied by the linear coefficients (a, b). The linear combination of past input and output value computes the one-step-ahead prediction of output value(y<sub>k+1</sub>).
Multiple iterations of the one-step-ahead prediction return the multi-step prediction (from y<sub>k+1</sub> to y<sub>k+n</sub>). The time window of the past input and output terms is shifted toward next segment for every iteration for multi-step prediction.
Here is an example formular with <img src="https://render.githubusercontent.com/render/math?math=\large n_a=3"> and <img src="https://render.githubusercontent.com/render/math?math=\large n_b=2"> for the single input and single output system,
<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large y_{k %2B 1}=a_{0} y_{k} %2B a_{1} y_{k-1} %2B a_{2} y_{k-2} %2B b_{0} u_{k} %2B b_{1} u_{k-1}" >
</p>

<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/Onestep-ahead.png" align="center" width="300" height="100">
</p>

ARX: Auto-Regressive with eXogenous input  
a: ARX coefficient for the past output value  
b: ARX coefficient for the past input value  
<img src="https://render.githubusercontent.com/render/math?math=\large n_a">: Number of terms for the past output value  
<img src="https://render.githubusercontent.com/render/math?math=\large n_b">: Number of terms for the past input value  
<img src="https://render.githubusercontent.com/render/math?math=\large n_c">: Delay between input and output  
<img src="https://render.githubusercontent.com/render/math?math=\large k">: present time step  
Here is another example formular with **delay** ($na=$3, $nb=$2, $nk=$2),  

<p align="center">
<img src="https://render.githubusercontent.com/render/math?math=\large y_{k+1}=a_{1} y_{k}+a_{2} y_{k-1}+a_{3} y_{k-2}+b_{1} u_{k-2}+b_{2} u_{k-1-2}" >
</p>

$y_{k+1}=a_{1} y_{k}+a_{2} y_{k-1}+a_{3} y_{k-2}+b_{1} u_{k-2}+b_{2} u_{k-1-2}$  



Although the ARX model can be more detailed by increasing the number of terms ($na$, $nb$), it could result in an overfit. Thus, it could be an essential step to compare the training and validation set, ensuring the prediction for the validation set is as good as the training set. The model fitting can be quantified using different statistical methods such as **MSE** (Mean Squared Error) or **SSE** (Sum of Squared Error)







## Overview
<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/overview0.jpg" align="center" width="800" height="602">
</p>
<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/overview1.png" align="center" width="800" height="450">
</p>
<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/overview2.png" align="center" width="800" height="450">
</p>
<p align="center">
<img src="https://github.com/BYU-PRISM/Seeq/blob/main/docs/images/overview3.png" align="center" width="800" height="450">
</p>

# User Guide

https://user-images.githubusercontent.com/55245976/136423446-9babb1da-41e6-4fcc-8bc0-066f98fc189d.mp4

[**SeeQ-System Identification User Guide**](https://github.com/BYU-PRISM/Seeq/blob/main/README.md)
provides a more in-depth explanation of System Identification and how seeq-System Identification works

----

# Installation

The backend of **seeq-System Identification** requires **Python 3.7** or later.

## Dependencies

See [`requirements.txt`](https://github.com/seeq12/seeq-correlation/tree/master/requirements.txt) file for a list of
dependencies and versions. Additionally, you will need to install the `seeq` module with the appropriate version that
matches your Seeq server. For more information on the `seeq` module see [seeq at pypi](https://pypi.org/project/seeq/)

## User Installation Requirements (Seeq Data Lab)

If you want to install **seeq-correlation** as a Seeq Add-on Tool, you will need:

- Seeq Data Lab (>= R50.5.0, >=R51.1.0, or >=R52.1.0)
- `seeq` module whose version matches the Seeq server version
- Seeq administrator access
- Enable Add-on Tools in the Seeq server

## User Installation (Seeq Data Lab)

The latest build of the project can be found [here](https://pypi.seeq.com/) as a wheel file. The file is published as a
courtesy to the user, and it does not imply any obligation for support from the publisher. Contact
[Seeq](mailto:applied.research@seeq.com?subject=[seeq-correlation]%20General%20Question) if you required credentials to
access the site.


https://user-images.githubusercontent.com/55245976/136426388-6b44382e-9542-4239-a43a-2cd49d667c3d.mp4


1. Create a **new** Seeq Data Lab project and open the **Terminal** window
2. Run `pip install seeq-correlation --extra-index-url https://pypi.seeq.com --trusted-host pypi.seeq.com`
3. Run `python -m seeq.addons.correlation [--users <users_list> --groups <groups_list>]`

----

# Development

We welcome new contributors of all experience levels. The **Development Guide** has detailed information about
contributing code, documentation, tests, etc.

## Important links

* Official source code repo: https://github.com/seeq12/seeq-correlation
* Issue tracker: https://github.com/seeq12/seeq-correlation/issues

## Source code

You can get started by cloning the repository with the command:

```shell
git clone git@github.com:seeq12/seeq-correlation.git
```

## Installation from source

For development work, it is highly recommended creating a python virtual environment and install the package in that
working environment. If you are not familiar with python virtual environments, you can take a
look [here](https://docs.python.org/3.8/tutorial/venv.html)

Once your virtual environment is activated, you can install **seeq-correlation** from source with:

```shell
python setup.py install
```

## Testing

There are several types of testing available for **seeq-correlation**

### Automatic Testing

After installation, you can launch the test suite from the root directory of the project (i.e. `seeq-correlation`
directory). You will need to have pytest >= 5.0.1 installed

To run all tests:

```shell
pytest
```

There are several pytest markers set up in the project. You can find the description of the marks in the `pytest.ini`
file. You can use the `-m` flag to run only a subset of tests. For example, to run only the `backend` tests, you can
use:

```shell
pytest -m backend
```

The integration tests requires a connection to a Seeq server. The tests are configured to try to access a local Seeq
server with the data directory set up in `ProgramData/Seeq/data` of the local drive. However, you can set the
`seeq_url`, `credentials_file` configuration options in the `test_config.ini` file to run the integration tests on a
remote Seeq server, or change the local seeq data directory with `data_dir`.

*Note:* Remember that the `seeq` module version in your local environment should match the Seeq server version

### User Interface Testing

To test the UI, use the `developer_notebook.ipynb` in the `development` folder of the project. This notebook can also be
used while debugging from your IDE. You can also create a whl first, install it on your virtual environment, and then
run `developer_notebook.ipynb` notebook there.

----

# Changelog

<!-- The change log can be found [**here**](https://seeq12.github.io/seeq-correlation/changelog.html) -->


----

# Support

Code related issues (e.g. bugs, feature requests) can be created in the
[issue tracker](https://github.com/BYU-PRISM/Seeq/issues)
Any other general comments or questions (non-code related) can be emailed to
[Seeq](mailto:applied.research@seeq.com?subject=[seeq-correlation]%20General%20Question)

<!-- Maintainer: Alberto Rivas -->


----

# Citation

Please cite this work as:

```shell
seeq-correlation v0.0.20
Seeq Corporation, 2021
https://github.com/BYU-PRISM/Seeq
```




