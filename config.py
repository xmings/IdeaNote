#!/bin/python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: wangms
# @Date  : 2018/8/7
import os
from datetime import timedelta, datetime


class BaseConfig(object):
    PROJECT_PATH = os.path.dirname(__file__)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False
    JSON_AS_ASCII = False
    CATALOG_JSON = ''
    SECRET_KEY = '123456789'
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}\\ideanote.db?check_same_thread=False'.format(PROJECT_PATH)
    REMOTE_URL = "git@git.coding.net:wmsgood/MyNote2.git"
    LOG_FILE = os.path.join(PROJECT_PATH, "log", "{}.log".format(datetime.now().strftime("%Y-%m-%d")))
    CREATE_DB_IF_NOT_FOUND = True


class ProductConfig(BaseConfig):
    pass

