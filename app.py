#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/6

from flask import Flask
from config import BaseConfig
from model import db
from core import core
import logging


import win32api, win32gui
ct = win32api.GetConsoleTitle()
hd = win32gui.FindWindow(0,ct)
win32gui.ShowWindow(hd,0)


app = Flask(__name__)
app.config.from_object(BaseConfig)
db.init_app(app)

logFile = app.config.get("LOG_FILE")
handler = logging.FileHandler(logFile)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
app.logger.addHandler(handler)

app.register_blueprint(core)

# app.app_context().push()
# db.drop_all()
# db.create_all()


if __name__ == '__main__':
    import sys
    assert len(sys.argv) == 3
    port, notes = sys.argv[1:]
    app.config['NOTES_DIRCTORY'] = notes
    app.run(port=port, threaded=True)
