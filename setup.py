#!/usr/bin/env python
from setuptools import setup

setup(
    name='netcli',
    version='1.0',
    packages=['netcli'],
    include_package_data=True,
    install_requires=[
        'pygments>=2.0.2',
        'prompt_toolkit>=1.0.0,<1.1.0',
        'click>=4.0',
        'fuzzyfinder>=1.0.0'
    ],
    entry_points={
        'console_scripts': [
            'netcli = netcli.main:cli',
        ]
    },
    url='https://github.com/QuantumEnergyE/netcli',
    author='quantum',
    author_email='quantumenergye@gmail.com ',
)
