#!/bin/python
# -*- coding: utf-8 -*-
# @File  : test_github_sync_utils.py
# @Author: wangms
# @Date  : 2019/12/21
import sys
from sync.sync_utils.github_sync_utils import GithubSyncUtils

if __name__ == '__main__':
    from common import conf
    sync_utils = GithubSyncUtils(conf.sync_connection_info)
    sync_utils.init_version_info()


