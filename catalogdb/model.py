#!/bin/python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: wangms
# @Date  : 2019/5/9
# @Brief: 简述报表功能
from dataclasses import dataclass
from datetime import datetime

@dataclass(order=True)
class Catalog(object):
    items: list
    modification_time: datetime
    version: int
    items_hash: str
    lock_item_ids: list
    users: dict


@dataclass(order=True)
class Item(object):
    id: int
    title: str
    type: str
    parent_id: int
    children: list
    icon_path: str
    file_path: str
    file_hash: str
    status: int
    creation_time: datetime
    modification_time: datetime


@dataclass(order=True)
class User(object):
    username: str
    password: str
    login_time: datetime
    login_host: str
    edit_item_id: int
    edit_start_time: datetime



