#!/bin/python
# -*- coding: utf-8 -*-
# @File  : netdisk_sync_utils.py
# @Author: wangms
# @Date  : 2019/8/8
# @Brief: 简述报表功能
import json
import os
import socket
import pickle
from datetime import datetime
from sync.sync_utils.base_sync_utils import BaseSyncUtils


class NetDiskSyncUtils(BaseSyncUtils):
    def __init__(self, work_dir):
        self.work_dir = work_dir
        self.version_info_file = os.path.join(self.work_dir, "version_info.json")
        self.note_info_file_suffix = ".note"

    def init_version_info(self):
        with open(self.version_info_file, "w", encoding="utf8") as f:
            f.write(json.dumps({
                "latest_version": 0,
                "client_id": socket.gethostname(),
                "change_time": datetime.now().isoformat()
            }, ensure_ascii=False, indent=4))

    def load_version_info(self) -> dict:
        with open(self.version_info_file, "r", encoding="utf8") as f:
            return json.loads(f.read())

    def dump_version_info(self, version_info: dict) -> bool:
        with open(self.version_info_file, "w", encoding="utf8") as f:
            f.write(json.dumps(version_info, ensure_ascii=False, indent=4))
        return True

    def load_note_info(self, version: int) -> dict:
        for filename in os.listdir(self.work_dir):
            if filename.endswith(self.note_info_file_suffix):
                version_id, note_id = os.path.splitext(filename)[0].split("-")
                if version == int(version_id):
                    note_info_file = os.path.join(self.work_dir, filename)
                    with open(note_info_file, "rb") as f:
                        return pickle.loads(f.read())
        return {}

    def load_latest_note_info(self, note_id) -> dict:
        latest_note_version = 0
        for filename in os.listdir(self.work_dir):
            if filename.find(note_id)>0 and filename.endswith(self.note_info_file_suffix):
                version_id, note_id = os.path.splitext(filename)[0].split("-")
                latest_note_version = max(version_id, latest_note_version)

        note_info_file = os.path.join(self.work_dir, f"{latest_note_version}-{note_id}{self.note_info_file_suffix}")

        if os.path.isfile(note_info_file):
            with open(note_info_file, "rb") as f:
                return pickle.loads(f.read())
        return {}


    def dump_note_info(self, note_info: dict) -> bool:
        filename = f"{note_info.get('version')}-{note_info.get('id')}{self.note_info_file_suffix}"
        note_info_file = os.path.join(self.work_dir, filename)
        with open(note_info_file, "wb") as f:
            f.write(pickle.dumps(note_info))
        return True

    def fetch_sync_note_list(self):
        note_version_list = os.listdir(self.work_dir)
        note_version_list.remove(os.path.basename(self.version_info_file))
        return note_version_list
