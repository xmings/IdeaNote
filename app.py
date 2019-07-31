#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/6

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask.logging import default_handler
from config import BaseConfig
from core import core
from onedrive import onedrive
from logging.config import dictConfig as loggerConfig


import win32api, win32gui
ct = win32api.GetConsoleTitle()
hd = win32gui.FindWindow(0,ct)
win32gui.ShowWindow(hd,0)


app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy()
db.init_app(app)

log_file = app.config.get("LOG_FILE")


@app.route('/static/js/<path:path>', methods=["GET"])
def send_js(path):
    return send_from_directory('static/js', path, mimetype="application/javascript")

loggerConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s %(levelname)s %(module)s %(lineno)d: %(message)s',
    }},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': app.config.get("LOG_FILE"),
            'level': 'INFO'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
})


app.register_blueprint(core)
app.register_blueprint(onedrive)

app.logger.removeHandler(default_handler)

# app.app_context().push()
# db.drop_all()
# db.create_all()


if __name__ == '__main__':
    import sys
    assert len(sys.argv) == 3
    port, notes = sys.argv[1:]
    app.config['NOTES_DIRCTORY'] = notes
    app.run(port=port, threaded=True)
