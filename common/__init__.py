#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/7/23
from enum import Enum
from common.utils import conf, timestamp_from_str, timestamp_to_str, timestamp_max, fetch_logger, Resp

class SyncStatusEnum(Enum):
    has_sync = 1
    need_sync = 2

class NoteStatusEnum(Enum):
    create = 1
    update_title = 2
    update_content = 3
    update_position = 4
    update_lock = 5
    need_merge = 6
    delete = -1


class PasswordStatusEnum(Enum):
    no_password = 0
    has_password = 1

class Result(object):
    def __init__(self, status, content=None):
        self.status = status
        self.content = content


__all__ = ("Result", "conf", "timestamp_from_str", "timestamp_to_str", "timestamp_max", "fetch_logger", "Resp")