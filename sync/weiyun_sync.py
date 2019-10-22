#!/bin/python
# -*- coding: utf-8 -*-
# @File  : weiyun_sync.py
# @Author: wangms
# @Date  : 2019/8/8
# @Brief: 简述报表功能
import json
import os
import socket
import time
from datetime import datetime, timedelta
from threading import Lock

sync_verion_lock = Lock()
sync_metadata_lock = Lock()


class WeiYunSync(object):
    def __init__(self, work_dir, sync_frequence=60):
        self.work_dir = work_dir
        self.sync_frequence = sync_frequence
        self.change_record_prefix = os.path.join(self.work_dir, "change_record")
        self.sync_metadata_file = os.path.join(self.work_dir, "sync.metadata")

        # 用于记录当前节点同步的version
        self.sync_version = None
        # 用于记录目前change_record中最大可用的version
        self.max_sync_version = None
        self.node_name = socket.gethostname()
        self.max_file_record_count = 2000
        # 用于记录当前节点上次同步变更的记录的最大时间点
        self.sync_timestamp = None

    def flush_sync_metadata(self, writing_node=None,
                            last_update_timestamp=None, sync_version=None, sync_timestamp=None):
        assert os.path.exists(self.sync_metadata_file)

        with sync_metadata_lock:
            with open(self.sync_metadata_file, "r") as f:
                metadata = json.loads(f.read())

            if writing_node:
                metadata["writing_node"] = writing_node

            if last_update_timestamp:
                metadata["last_update_timestamp"] = last_update_timestamp

            if sync_timestamp:
                metadata["sync_timestamp"][self.node_name] = sync_timestamp

            if sync_version:
                metadata["sync_version"][self.node_name] = sync_version

            if writing_node or last_update_timestamp or sync_version or sync_timestamp:
                with open(self.sync_metadata_file, "w") as f:
                    f.write(json.dumps(metadata))

            self.sync_version = metadata.get("sync_version").get(self.node_name)
            self.sync_timestamp = metadata.get("sync_timestamp").get(self.node_name)
            self.max_sync_version = max(metadata.get("sync_version").values())

        return metadata

    def dump_note(self, note):
        with sync_verion_lock:
            self.sync_version += 1

            file_no = (self.sync_version // self.max_file_record_count) * self.max_file_record_count
            with open(f"{self.change_record_prefix}.{file_no}", "a") as f:
                f.write(json.dumps({
                    "type": "note",
                    "version": self.sync_version,
                    "id": note.id,
                    "title": note.title,
                    "icon": note.icon,
                    "parent_id": note.parent_id,
                    "seq_no": note.seq_no,
                    "status": note.status,
                    "creation_time": str(note.creation_time),
                    "modification_time": str(note.modification_time)
                }))

            note_file = os.path.join(self.work_dir, f"{note.id}-{self.sync_version}.note")
            with open(note_file, "wb") as f:
                f.write(note.content)

    def dump_images(self, image):
        with sync_verion_lock:
            self.sync_version += 1
            file_no = (self.sync_version // self.max_file_record_count) * self.max_file_record_count
            with open(f"{self.change_record_prefix}.{file_no}", "a") as f:
                f.write(json.dumps({
                    "type": "image",
                    "version": self.sync_version,
                    "id": image.id,
                    "note_id": image.note_id,
                    "mime_type": image.mime_type,
                    "status": image.status,
                    "creation_time": image.creation_time,
                    "modification_time": image.modification_time
                }))

            img_file = os.path.join(self.work_dir, f"{image.id}-{self.sync_version}.img")
            with open(img_file, "wb") as f:
                f.write(image.image)

    def load_change_record(self, last_change_timestamp):
        self.flush_sync_metadata()

        assert last_change_timestamp == self.sync_timestamp

        start_file_no = (self.sync_version // self.max_file_record_count) * self.max_file_record_count
        end_file_no = (self.max_sync_version // self.max_file_record_count + 1) * self.max_file_record_count

        for file_no in range(start_file_no, end_file_no, self.max_file_record_count):
            change_record_file = f"{self.change_record_prefix}.{file_no}"
            with open(change_record_file, "r") as f:
                for line in f.readlines():
                    record = json.loads(line)
                    if int(record.get("sync_version")) > self.sync_version:
                        yield record

    def load_note(self, note_id, version):
        note_file = os.path.join(self.work_dir, f"{note_id}-{version}.note")
        with open(note_file, "rb") as f:
            return f.read()

    def load_image(self, image_id, version):
        note_file = os.path.join(self.work_dir, f"{image_id}-{version}.note")
        with open(note_file, "rb") as f:
            return f.read()

    def request_push_lock(self, block=False):
        metadata = self.flush_sync_metadata()

        if metadata.get("writing_node") == self.node_name:
            self.flush_sync_metadata(writing_node=self.node_name, last_update_timestamp=datetime.now())
            return True

        last_update_time = metadata.get("last_update_time")
        time.sleep(self.sync_frequence * 3)

        while block:
            metadata = self.flush_sync_metadata()
            if last_update_time == metadata.get("last_update_time"):
                self.flush_sync_metadata(writing_node=self.node_name, last_update_timestamp=datetime.now())
                return True

            time.sleep(self.sync_frequence)
        return False

    def cleanup_expired_note(self):
        metadata = self.flush_sync_metadata()
        min_version = min(metadata.get("sync_version").values())
        min_version = (min_version // self.max_file_record_count) * self.max_file_record_count

        if self.request_push_lock():
            for filename in os.listdir(self.work_dir):
                prefix, subffix = filename.split(".")
                if prefix.startswith(os.path.basename(self.change_record_prefix)):
                    if int(subffix) < min_version:
                        os.remove(os.path.join(self.work_dir, filename))
                else:
                    xid, version = prefix.split("-")
                    if int(version) < min_version:
                        os.remove(os.path.join(self.work_dir, filename))
