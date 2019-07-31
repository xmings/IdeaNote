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
        self.remote_metadata = {}
        self.local_metadata = {}

    def fetch_remote_metadata(self):
        pass

    def metadata_version_interval(self, local_metadata):
        pass

    def merge_metadata(self):
        pass

    def create_diff_record(self):
        pass

    def fetch_remote_path_content(self, path):
        pass

    def update_remote_note_content(self, path, sha, content):
        pass

    def delete_remote_note(self, path, sha):
        pass





