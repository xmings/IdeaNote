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
    SQLALCHEMY_ECHO = True
    JSON_AS_ASCII = False
    CATALOG_JSON = ''
    SECRET_KEY = '123456789'
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)
    NOTES_DIRCTORY = "D:\\MyNote"
    IMAGE_FOLDER = ".img"
    ITEM_FILE_SUFFIX = ".md"
    FOLDER_CONTENT_FILE = "init.md"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}\\ideanote.db?check_same_thread=False'.format(NOTES_DIRCTORY)
    REMOTE_URL = "https://git.coding.net/wmsgood/new_mynote.git"
    LOG_FILE = os.path.join(PROJECT_PATH, "log", "{}.log".format(datetime.now().strftime("%Y-%m-%d")))
    JSON_DB_FILE = os.path.join(NOTES_DIRCTORY, "ideanote.json")
    CREATE_DB_IF_NOT_FOUND = True



    # db.create_all(bind=['users'])
    # __bind_key__ = 'users'


class ProductConfig(BaseConfig):
    pass

