#!/bin/python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: wangms
# @Date  : 2018/8/7
import os
from datetime import timedelta, datetime


class BaseConfig(object):
    PROJECT_PATH = os.path.abspath('.')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = True
    JSON_AS_ASCII = False
    CATALOG_JSON = ''
    SECRET_KEY = '123456789'
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)
    NOTES_DIRCTORY = os.path.join(PROJECT_PATH, 'notes')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}\\ideanote.db?check_same_thread=False'.format(NOTES_DIRCTORY)
    MYTOKEN = os.getenv("MYTOKEN")
    DB_USER = "xmings"
    DB_PASS = "xmings"
    REMOTE_URL = "git@github.com:xmings/xmings.github.io.git"
    LOG_FILE = os.path.join(PROJECT_PATH, "log", "{}.log".format(datetime.now().strftime("%Y-%m-%d")))


    # db.create_all(bind=['users'])
    # __bind_key__ = 'users'


class ProductConfig(BaseConfig):
    pass

