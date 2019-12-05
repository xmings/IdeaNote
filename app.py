#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/6
import os, platform
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from common import conf
from logging import INFO, Formatter, basicConfig
from logging.handlers import TimedRotatingFileHandler

if platform.system() == "Windows" and conf.hide_window:
    import win32api, win32gui
    ct = win32api.GetConsoleTitle()
    hd = win32gui.FindWindow(0,ct)
    win32gui.ShowWindow(hd,0)


app = Flask(__name__)
app.config.from_mapping(conf.db_config)
app.config['SECRET_KEY'] = "12345"
log_handler = TimedRotatingFileHandler(
    filename=os.path.join(conf.log_directory, "idea_note.log"),
    when="midnight",
    encoding="utf8"
)
log_handler.setLevel(INFO)
log_handler.setFormatter(Formatter(conf.log_formatter))
basicConfig(format=conf.log_formatter, datefmt=None)
app.logger.addHandler(log_handler)

db = SQLAlchemy(app)

@app.route('/static/js/<path:path>', methods=["GET"])
def send_js(path):
    return send_from_directory('static/js', path, mimetype="application/javascript")


from core import core
app.register_blueprint(core)

# app.app_context().push()
# db.drop_all()
# db.create_all()


if __name__ == '__main__':
    app.run(port=conf.app_port, threaded=True)
