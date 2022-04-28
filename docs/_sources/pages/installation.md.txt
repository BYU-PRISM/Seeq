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

- Seeq Data Lab (>= R50.5.0, >=R51.1.0, or >=R52.1.0)
- `seeq` module whose version matches the Seeq server version
- Seeq administrator access
- Enable Add-on Tools (or External Tools) in the Seeq server

## User Installation (Seeq Data Lab)

<details open="" class="details-reset border rounded-2">
  <summary class="px-3 py-2 border-bottom">
    <svg aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-device-camera-video">
    <path fill-rule="evenodd" d="M16 3.75a.75.75 0 00-1.136-.643L11 5.425V4.75A1.75 1.75 0 009.25 3h-7.5A1.75 1.75 0 000 4.75v6.5C0 12.216.784 13 1.75 13h7.5A1.75 1.75 0 0011 11.25v-.675l3.864 2.318A.75.75 0 0016 12.25v-8.5zm-5 5.075l3.5 2.1v-5.85l-3.5 2.1v1.65zM9.5 6.75v-2a.25.25 0 00-.25-.25h-7.5a.25.25 0 00-.25.25v6.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-4.5z"></path>
    </svg>
    <span aria-label="https://user-images.githubusercontent.com/55245976/137494969-43d93065-1e23-4e7c-952f-2397993eb269.mp4" class="m-1">SysID Add-on Installation</span>
    <span class="dropdown-caret"></span>
  </summary>

<video src="https://user-images.githubusercontent.com/55245976/137494969-43d93065-1e23-4e7c-952f-2397993eb269.mp4"
controls="controls" muted="muted" class="d-block rounded-bottom-2 width-fit" style="max-width:700px; width:100%;"
webboost_found_paused="true" webboost_processed="true">
</video>
</details>

1. Create a **new** Seeq Data Lab project and open the **Terminal** window
2. Run `pip install seeq-sysid`
3. Upload **sysid_notebook.ipynb** file to the Seeq Data Lab project.

For more information about adding this addon to the seeq workbench
[click here](https://seeq.atlassian.net/wiki/spaces/KB/pages/961675391/Add-on+Tool+Administration+and+Development).

## Developer Installation

For development work, after checking out the code from the repository,
it is highly recommended you create a python virtual environment, 
`pip install -r requirement.txt`, and install the package in that
working environment. If you are not familiar with python virtual environments,
it is recommended you take a look [here](https://docs.python.org/3.8/tutorial/venv.html).

Once your virtual environment is activated, you can install **seeq-sysid** from source with:

```shell
python setup.py install
```

Or build a `.whl` file using the following command

```shell
python setup.py bdist_wheel
```

and then `pip install [FILE NAME].whl`
(the `wheel` file name can change depending on the version).

There is a template for the developer notebook in `/deployment_notebook`.
Next, modify the parameters within the workbook for your local environment (username, password, workbook, worksheet, etc.).
Finally, start a jupyter server and navigate to the development notebook in the root directory.

```sh

$ jupyter notebook

```
