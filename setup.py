#!/bin/python
# -*- coding: utf-8 -*-
# @File  : setup.py
# @Author: wangms
# @Date  : 2019/1/12
from setuptools import find_packages, setup

setup(
    name='IdeaNote',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'Flask-SQLAlchemy'
    ],
)