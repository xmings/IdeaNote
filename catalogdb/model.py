#!/bin/python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: wangms
# @Date  : 2019/5/9
# @Brief: 简述报表功能
import re
from dataclasses import dataclass, field
from datetime import datetime

from dateutil.parser import parse as datetimeparser


@dataclass(order=True)
class Catalog(object):
    items: list
    modification_time: datetime
    version: int
    items_hash: str
    lock_item_ids: list
    users: dict

    def __setattr__(self, key, value):
        if isinstance(value, str) and key.endswith("time"):
            self.__dict__[key] = datetimeparser(value)
            return
        self.__dict__[key] = value

@dataclass(order=True)
class Item(object):
    title: str
    parent_id: int
    icon_path: str = ""
    file_path: str = ""
    file_hash: str = ""
    id: int = None
    status: int = 1
    children: list = field(repr=False, default_factory=list)
    creation_time: datetime = datetime.now()
    modification_time: datetime = datetime.now()

    def __setattr__(self, key, value):
        if isinstance(value, str) and key.endswith("time"):
            self.__dict__[key] = datetimeparser(value)
            return
        self.__dict__[key] = value


@dataclass(order=True)
class User(object):
    username: str
    password: str
    regist_time: datetime
    login_time: datetime = None
    login_host: str = None
    edit_item_id: int = None
    edit_start_time = None


    def __setattr__(self, key, value):
        if isinstance(value, str) and key.endswith("time"):
            self.__dict__[key] = datetimeparser(value)
            return
        self.__dict__[key] = value

if __name__ == '__main__':
    user = User(
        username='w', password='w', regist_time='2019-05-12 12:00:00'
    )
    print(user)