#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/6

from flask import Flask
from config import BasConfig
from model import db
from core import core


app = Flask(__name__)
app.config.from_object(BasConfig)
db.init_app(app)
app.register_blueprint(core)


if __name__ == '__main__':
    app.run()
