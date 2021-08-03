[![N|Solid](https://www.seeq.com/sites/default/files/seeq-logo-navbar-small.png)](https://www.seeq.com)

**add-on-template** is a Python dummy module that examplifies how to develop a Seeq Add-on and register it in Workbench

----
# Installation
The backend of **add-on-template** requires **Python >3.7**

## Dependencies

- ipyvuetify >= 1.5.1
- pandas >= 1.2.1


## User Installation Requirements (Seeq Data Lab)
If you want to install **add-on-template** as a Seeq Add-on Tool, you will need:

- Seeq Data Lab (> R50.5.0, >R51.1.0, or >R52.1.0)
- `seeq` module whose version matches the Seeq server version
- Seeq server admin access
- Enable Add-on Tools in the Seeq server

## User Installation (Seeq Data Lab)
1. Create a **new** Seeq Data Lab project and open the **Terminal** window
2. Run `pip install my-addon-name`
3. Run `python -m companynamespace.addons.mypackage [--users <users_list> --groups<groups_list>]`
----


## Important links
* Official source code repo: URL
* Download releases: URL
* Issue tracker: URL

## Source code
You can get started by cloning the repository with the command:
```shell
git clone git@repo_name.git
```

## Installation from source
You can directly install the package on your virtual environment with:
```shell
python setup.py install
```
Alternatively, you can build a wheel file first and then `pip install` it in your venv

```shell
python setup.py bdist_wheel
```

## Testing
There are several types of testing available for **add-on-template**

### Automatic Testing
After installation, you can launch the test suite from outside the source directory 
(you will need to have pytest >= 5.0.1 installed):

```shell
pytest
```

### User Interface Testing
To test the UIs, use the `developer_notebook.ipynb` in the `development` folder of the project. This notebook
can also be used while debugging from your IDE. You can also create a whl first, install it on your preferred 
virtual environment, and then run `developer_notebook.ipynb` notebook there.

----
# Documentation

Your documentation goes here

-----

# Changelog
Record feature changes and bug fixes


----
# Support
Contact information







