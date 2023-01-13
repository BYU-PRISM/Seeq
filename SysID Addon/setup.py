from setuptools import setup, find_packages

with open(file='README.md', mode='r') as readme_handle:
    long_description = readme_handle.read()

setup(
    name='seeq_sysid',
    version='0.6.1',
    packages=find_packages(),
    url='https://github.com/BYU-PRISM/Seeq',
    license='MIT',
    author='Junho Park, Mohammad Reza Babaei',
    author_email='jnho.park@gmail.com, babaei_mr@outlook.com',
    description='Seeq System Identification Addon',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
	  'ipyvuetify>=1.5.1',
	  'gekko~=1.0.5',
	  'numpy~=1.21.5',
	  'pandas>=1.2.1',
	  'plotly>=4.5.0',
       'python-dateutil>=2.8.1',
	  'tensorflow~=2.5',
	  'keras-tuner==1.0.4',
	  'scipy'
    ],
    keywords='Seeq Prism System Identification ARX FIR ARIMAX Subspace State-Space Neural-Network Addon Time-Series Transfer Function',
    include_package_data=True,
    package_data={'seeq_sysid': ['data/seeq_logo.png']},
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ]
)
