#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py
# @Author: wangms
# @Date  : 2018/8/7
from flask import Blueprint

core = Blueprint('core', __name__)

from . import view