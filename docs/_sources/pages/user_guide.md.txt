# User Guide
## How to Use

SysID is launched from within Seeq Workbench after creating a worksheet and adding the signals to the worksheet. System identification is performed on a single worksheet and includes all of the available signals and manual conditions.


## Workflow

1. Add all relevant dataset signals to the trend view. Set the time range as desired. The data range should be long enough to capture significant variation in the signal. In the other words, selected data should be rich that represent all of the dynamics of the system. Also, selecting a long range of data may slow down the identification and simulation process.

2. To improve the model quality and response time, select the training and validation conditions. (Optional)

<p align='center'>
<a href="../_static/create_condition.gif">
<img alt="image" src="../_static/create_condition.gif" width=80%></a>
</p>

3. From the Tools tab in Workbench, select Add-ons. Then click on System Identification.

4. Modify the model setup and click on 'Identify'. 

5. Validate the model and push the results to Workbench.

## Interface

[![User Interface](../_static/interface.gif)](../_static/interface.gif)

### App Bar
Contains Model Tabs, Seeq Logo and Hamburger Menu (App Menu)

#### Model Tab
Switch between different types of model that is available in Seeq SysID add-on.

#### Hamburger Menu
Contains a list of options like Load Worksheet, User Guide and Support.

### Left Panel
The user can set up the model based on input/output signals and model complexity in this panel. The training and validation conditions can be selected in this section.

### Figure
The prediction results for both training and validation conditions are shown in this panel.

### Table
In this section, The user can show/hide each available signal. Also, there are options to change the style of each line.
