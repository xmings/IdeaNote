#!/bin/python
# -*- coding: utf-8 -*-
# @File  : utils.py
# @Author: wangms
# @Date  : 2019/7/27
import os
import yaml

class ConfigLoader(object):
    def __init__(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(project_root, "config.yml"), "r", encoding="utf8") as f:
            self.config = yaml.load(f.read(), Loader=yaml.FullLoader)

    @property
    def remote_connection_info(self):
        return self.config.get("IdeaNote").get("sync").get("remote").get("connection")


conf = ConfigLoader()