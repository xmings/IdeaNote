#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/6

from flask import Flask
from config import BaseConfig
from model import db
from core import core


app = Flask(__name__)
app.config.from_object(BaseConfig)
db.init_app(app)
app.register_blueprint(core)

# app.app_context().push()
# db.drop_all()
# db.create_all()


if __name__ == '__main__':
    app.run()
