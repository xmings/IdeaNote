#!/bin/python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: wangms
# @Date  : 2019/5/9
# @Brief: 简述报表功能
from dataclasses import dataclass, field
from datetime import datetime

from dateutil.parser import parse as datetimeparser

@dataclass
class BaseModel(object):
    def __setattr__(self, key, value):
        property_type = self.__class__.__dict__.get('__annotations__').get(key)
        if property_type is datetime and isinstance(value, str):
            value = datetimeparser(value)
        self.__dict__[key] = value

    def __post_init__(self):
        for key, value in self.__dict__.items():
            setattr(self, key, value)

@dataclass(order=True)
class Catalog(BaseModel):
    items: list
    modification_time: datetime
    version: int
    items_hash: str
    lock_item_ids: list
    users: dict


@dataclass(order=True)
class Item(BaseModel):
    title: str
    parent_id: int
    icon_path: str = ""
    file_path: str = ""
    file_hash: str = ""
    id: int = None
    type: str = "file"
    status: int = 1
    children: list = field(repr=False, default_factory=list)
    creation_time: datetime = datetime.now()
    modification_time: datetime = None



@dataclass(order=True)
class User(BaseModel):
    username: str
    password: str
    regist_time: datetime
    login_time: datetime = None
    login_host: str = None
    edit_item_id: int = None
    edit_start_time = None
