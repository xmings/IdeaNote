#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/7/23
from enum import IntEnum
from common.utils import conf, timestamp_from_str, timestamp_to_str, timestamp_max, fetch_logger, Resp


class SyncStatusEnum(IntEnum):
    has_sync = 1
    need_sync = 2


class NoteStatusEnum(IntEnum):
    create = 1
    update_title = 2
    update_content = 3
    update_position = 4
    update_lock = 5
    need_merge = 6
    manual_sync = 7
    delete = -1


class PasswordStatusEnum(IntEnum):
    no_password = 0
    has_password = 1


class Result(object):
    def __init__(self, status, content=None):
        self.status = status
        self.content = content


status_text_mapping = {
    NoteStatusEnum.create.value: "新建笔记",
    NoteStatusEnum.update_title.value: "更新标题",
    NoteStatusEnum.update_content.value: "更新内容",
    NoteStatusEnum.update_lock.value: "更新密码",
    NoteStatusEnum.update_position.value: "更新顺序",
    NoteStatusEnum.manual_sync.value: "手工同步",
    NoteStatusEnum.delete.value: "删除笔记"
}

__all__ = ("Result", "conf", "timestamp_from_str", "timestamp_to_str", "timestamp_max", "fetch_logger", "Resp")
