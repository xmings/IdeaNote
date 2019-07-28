#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/7/28
from flask import Blueprint

onedrive = Blueprint('onedrive', __name__)

from . import view