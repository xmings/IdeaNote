#!/bin/python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: wangms
# @Date  : 2018/8/7
import os
from datetime import timedelta


class BaseConfig(object):
    PROJECT_PATH = os.path.abspath('.')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}\\ideanote.db?check_same_thread=False'.format(PROJECT_PATH)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = True
    JSON_AS_ASCII = False
    CATALOG_JSON = ''
    NOTES_DIRCTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes')
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)

    # db.create_all(bind=['users'])
    # __bind_key__ = 'users'


class ProductConfig(BaseConfig):
    pass

