#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/7/23
from common.utils import conf, timestamp_from_str, timestamp_to_str, timestamp_max

class Result(object):
    def __init__(self, status, content=None):
        self.status = status
        self.content = content


__all__ = ("Result", "conf", "timestamp_from_str", "timestamp_to_str", "timestamp_max")