from setuptools import setup
from setuptools import find_namespace_packages

with open(file='README.md', mode='r') as readme_handle:
    long_description = readme_handle.read()

setup(
    name='seeq_sysid',
    version='0.0.3',
    packages=['seeq_sysid'],
    url='https://github.com/BYU-PRISM/Seeq',
    license='LICENSE',
    author='Mohammad Reza Babaei, Junho Park',
    author_email='babaei_mr@outlook.com, jnho.park@gmail.com',
    description='Seeq System Identification Addon',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'ipyvuetify',
        'pandas',
        'plotly',
        'ipywidgets',
        'numpy',
        'gekko<=1.0.1',
        'statsmodels<=0.12.2',
        'setuptools<=49.2.1',
        'sippy-rcognita<=0.2.1',
        'seeq',
        'control<=0.9.0',
    ],
    keywords='Seeq, Prism, System Identification, ARX, Subspace, State Space, Addon, Time Series',
    include_package_data=True,
    package_data={'seeq_sysid': ['data/seeq_logo.png']},
    classifiers=[
        'License :: OSI Approved :: MIT License',

        'Natural Language :: English',

        'Programming Language :: Python',
    ]
)
