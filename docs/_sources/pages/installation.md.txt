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

*Note:* For older versions of Seeq Data Lab you can find installation guide [`here`](https://user-images.githubusercontent.com/55245976/137494969-43d93065-1e23-4e7c-952f-2397993eb269.mp4).
<!-- (>= R50.5.0, >=R51.1.0, or >=R52.1.0) -->


## User Installation (Seeq Data Lab)

<p>
<video width="100%" height="100%" controls>
  <source src="https://raw.githubusercontent.com/BYU-PRISM/Seeq/a587646abcbbf23d3be6ec2b148007ae32937c27/docs_src/source/_static/videos/Installation.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>
</p>

1. Create a **new** Seeq Data Lab project and open the **Terminal** window
2. Run `pip install seeq-sysid`
3. Run `python -m seeq_sysid [--users <users_list> --groups <groups_list>]`

For more information about adding this addon to the seeq workbench
[click here](https://seeq.atlassian.net/wiki/spaces/KB/pages/961675391/Add-on+Tool+Administration+and+Development).


## Developer Installation

For development work, after checking out the code from the repository,
it is highly recommended you create a python virtual environment, 
`pip install -r requirement.txt`, and install the package in that
working environment. If you are not familiar with python virtual environments,
it is recommended you take a look [here](https://docs.python.org/3.8/tutorial/venv.html).

Once your virtual environment is activated, you can install **seeq-sysid** from the source with:

```shell
python setup.py install --user
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
