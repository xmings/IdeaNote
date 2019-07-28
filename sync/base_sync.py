#!/bin/python
# -*- coding: utf-8 -*-
# @File  : base_sync.py
# @Author: wangms
# @Date  : 2019/7/27
"""
10分钟联网检查服务端元数据版本号，如果不同就获取差异note内容到本地，提示用户手工合并
"""


class BaseSync(object):
    def __init__(self):
        pass

    def fetchSrvMetaData(self):
        pass

    def isSameMainVer(self):
        pass

    def fetchDiffRecord(self):
        pass

    def fetchNoteContentById(self, id):
        pass





