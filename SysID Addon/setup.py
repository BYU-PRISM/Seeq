from setuptools import setup, find_packages

with open(file='README.md', mode='r') as readme_handle:
    long_description = readme_handle.read()

setup(
    name='seeq_sysid',
    version='1.0.2-dev0',
    packages=find_packages(),
    url='https://github.com/BYU-PRISM/Seeq',
    license='MIT',
    author='Junho Park, Mohammad Reza Babaei',
    author_email='jnho.park@gmail.com, babaei_mr@outlook.com',
    description='Seeq System Identification Addon',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
	  'ipyvuetify>=1.6.2',
	  'ipywidgets==7.7.2',
	  'gekko>=1.3.0',
	  'numpy>=1.26.4',
	  'pandas>=2.2.3',
	  'plotly==5.24.1',
      'python-dateutil>=2.8.1',
	  'tensorflow>=2.19.0',
	  'keras-tuner>=1.4.7',
	  'scipy>=1.16.0',
	  'scikit-learn>=1.7.1',
	  'protobuf>=5.29.5',
      'seeq',
	  'seeq-spy'
    ],
    keywords='Seeq Prism System Identification ARX FIR ARIMAX Subspace State-Space Neural-Network Addon Time-Series Transfer Function',
    include_package_data=True,
    package_data={'seeq_sysid': ['data/seeq_logo.png']},
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ]
)
