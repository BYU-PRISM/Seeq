# coding: utf-8
import re
from parver import Version, ParseError
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version_scope = {'__builtins__': None}
with open("companynamespace/addons/mypackage/_version.py", "r+") as f:
    version_file = f.read()
    version_line = re.search(r"__version__ = (.*)", version_file)
    if version_line is None:
        raise ValueError(f"Invalid version. Expected __version__ = 'xx.xx.xx', but got \n{version_file}")
    version = version_line.group(1).replace(" ", "").strip('\n').strip("'").strip('"')
    print(f"version: {version}")
    try:
        Version.parse(version)
        exec(version_line.group(0), version_scope)
    except ParseError as e:
        print(str(e))
        raise

setup_args = dict(
    name='my-addon-name',
    version=version_scope['__version__'],
    author="Jane Doe",
    author_email="Jane.Doe@company.com",
    # license="No license offered",
    platforms=["Linux", "Windows"],
    description="Short description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://company.com",
    packages=setuptools.find_namespace_packages(include=['companynamespace.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'ipyvuetify>=1.5.1',
        'numpy>=1.19.5',
        'pandas~=1.2.5',
        'plotly<=4.14.3',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

setuptools.setup(**setup_args)
