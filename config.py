#!/bin/python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: wangms
# @Date  : 2018/8/7
import os


class BasConfig(object):
    PROJECT_PATH = os.path.abspath('.')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}\\ideanote.db?check_same_thread=False'.format(PROJECT_PATH)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = True
    JSON_AS_ASCII = False

    # db.create_all(bind=['users'])
    # __bind_key__ = 'users'


class ProductConfig(BasConfig):
    pass

