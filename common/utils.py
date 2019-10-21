#!/bin/python
# -*- coding: utf-8 -*-
# @File  : utils.py
# @Author: wangms
# @Date  : 2019/7/27
import os
from dataclasses import dataclass, field
from datetime import datetime, date

import yaml
import json


class ConfigLoader(object):
    def __init__(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(project_root, "config.yml"), "r", encoding="utf8") as f:
            self.config = yaml.load(f.read(), Loader=yaml.FullLoader)

    @property
    def remote_connection_info(self):
        return self.config.get("IdeaNote").get("sync").get("remote").get("connection")

    @property
    def metadata_file(self):
        return self.config.get("IdeaNote").get("metadata_file")

    @property
    def note_data_path(self):
        return self.config.get("IdeaNote").get("note_data_path")

    @property
    def db_config(self):
        return self.config.get("IdeaNote").get("db").get("config")

    @property
    def log_directory(self):
        return self.config.get("IdeaNote").get("log").get("directory")

    @property
    def log_formatter(self):
        return self.config.get("IdeaNote").get("log").get("formatter")

    @property
    def app_port(self):
        return self.config.get("IdeaNote").get("port")

    @property
    def sync_work_dir(self):
        return self.config.get("IdeaNote").get("sync").get("work_dir")


conf = ConfigLoader()


@dataclass(order=True)
class Item(object):
    id: int
    title: str
    parent_id: int
    children: list = field(repr=False, default_factory=list)


class JsonEncoderForFrontEnd(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Item):
            if o.children:
                return {
                    "id": o.id,
                    "name": o.title,
                    "open": False,
                    "children": o.children
                }
            return {
                "id": o.id,
                "name": o.title,
                "open": False
            }
        return super().default(o)
