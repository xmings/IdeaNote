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

def timestamp_from_str(s):
    if s:
        return datetime.fromisoformat(s)
    return None

def timestamp_to_str(ts):
    if ts:
        return str(ts)
    return None

def timestamp_max(ts1, ts2):
    if ts1 is None:
        return ts2
    elif ts2 is None:
        return ts1
    return max(ts1, ts2)

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
    def flask_config(self):
        return self.config.get("IdeaNote").get("flask").get("config")

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

    @property
    def hide_window(self):
        return self.config.get("IdeaNote").get("hide_window")

    @property
    def urlmark_sync(self):
        return self.config.get("IdeaNote").get("urlmark").get("sync")

    @property
    def urlmark_file(self):
        return self.config.get("IdeaNote").get("urlmark").get("sync_file")

    @property
    def auth_code(self):
        return self.config.get("IdeaNote").get("auth_code")


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
