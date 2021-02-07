#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/6
import os, platform
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from common import conf, fetch_logger

if platform.system() == "Windows" and conf.hide_window:
    import win32api, win32gui

    ct = win32api.GetConsoleTitle()
    hd = win32gui.FindWindow(0, ct)
    win32gui.ShowWindow(hd, 0)

app = Flask(__name__)
app.config.from_mapping(conf.db_config)
app.config['SECRET_KEY'] = "12345"

logger = fetch_logger(logger_name="IdeaNote", log_filename="idea_note.log")
app.logger.handlers = logger.handlers

db = SQLAlchemy(app)


@app.route('/static/js/<path:path>', methods=["GET"])
def send_js(path):
    return send_from_directory('static/js', path, mimetype="application/javascript")


from sync import sync

app.register_blueprint(sync)

from core import core

app.register_blueprint(core)

# app.app_context().push()
# db.drop_all()
# db.create_all()


if __name__ == '__main__':
    app.run(port=conf.app_port, threaded=True)
