#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py
# @Author: wangms
# @Date  : 2019/5/28

from flask import Blueprint

sync = Blueprint('sync', __name__)

from . import view