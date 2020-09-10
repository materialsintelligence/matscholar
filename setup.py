# coding: utf-8
# Copyright (c) Matscholar Development Team.
# Distributed under the terms of the MIT License.

from setuptools import setup, find_packages
import sys
import platform

extra_link_args = []
if sys.platform.startswith('win') and platform.machine().endswith('64'):
    extra_link_args.append('-Wl,--allow-multiple-definition')

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='matscholar',
    version='0.0.3',
    description='matscholar: a Python library for interacting with the Materials Scholar database.',
    long_description=readme,
    author='Materials Scholar Development Team',
    author_email='jdagdelen@lbl.gov, vahe@tshitoyan.com, lweston@lbl.gov, ardunn@lbl.gov',
    url='https://github.com/materialsintelligence/matscholar',
    license=license,
    packages=find_packages(),
    install_requires=["numpy", "requests"]
)