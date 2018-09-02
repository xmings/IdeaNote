#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2018/8/6
from . import core
from flask import render_template


@core.route('/')
def hello_world():
    return render_template('editor-markdown.html')