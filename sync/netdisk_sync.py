#!/bin/python
# -*- coding: utf-8 -*-
# @File  : netdisk_sync.py
# @Author: wangms
# @Date  : 2019/8/8
# @Brief: 简述报表功能
import json
import os
import socket
import time
from datetime import datetime, timedelta
from threading import Lock
from common import timestamp_from_str, timestamp_to_str

sync_verion_lock = Lock()
sync_metadata_lock = Lock()


class NetDiskSync(object):
    def __init__(self, work_dir, sync_frequence=60):
        self.work_dir = work_dir
        self.sync_frequence = sync_frequence
        self.change_record_prefix = os.path.join(self.work_dir, "change_record")
        self.sync_metadata_file = os.path.join(self.work_dir, "sync.metadata")
        self.note_file_suffix = ".note"
        self.image_file_suffix = ".image"


        self._writing_node = None
        # 用于记录当前节点同步的version，作为变更日志应用过程中的offset
        self.sync_version = None
        # 用于记录目前change_record中最大可用的version，作为变更日志中的最大offset
        self.max_sync_version = None
        # 主要用于记录各节点最近一次产生变更日志的对应记录的时间(max(creation_time,modification_time))
        self.sync_timestamp = None

        self.last_update_timestamp = None


        self.node_name = socket.gethostname()
        self.max_file_record_count = 2000

    @property
    def writing_node(self):
        return self._writing_node

    def flush_sync_metadata(self):
        assert os.path.exists(self.sync_metadata_file)

        with sync_metadata_lock:
            with open(self.sync_metadata_file, "r") as f:
                metadata = json.loads(f.read())

            # 只有request_push_lock请求到锁时会给write_node赋值，
            # 另外，只有当dump_note或者dump_image时才给last_update_timestamp赋值
            if self.writing_node:
                metadata["writing_node"] = self.writing_node
                metadata["last_update_timestamp"] = timestamp_to_str(self.last_update_timestamp)

            if self.sync_timestamp:
                metadata["sync_timestamp"][self.node_name] = timestamp_to_str(self.sync_timestamp)
            else:
                self.sync_timestamp = timestamp_from_str(metadata["sync_timestamp"].get(self.node_name)) \
                                      or datetime.now() - timedelta(hours=10)

            if self.sync_version:
                metadata["sync_version"][self.node_name] = self.sync_version
            else:
                self.sync_version = metadata["sync_version"].get(self.node_name, 1)


            with open(self.sync_metadata_file, "w") as f:
                f.write(json.dumps(metadata, indent=4))

            self.max_sync_version = int(max(metadata.get("sync_version").values()))

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
                    "creation_time": timestamp_to_str(note.creation_time),
                    "modification_time": timestamp_to_str(note.modification_time)
                }, ensure_ascii=False) + "\n")

            note_file = os.path.join(self.work_dir, f"{note.id}-{self.sync_version}{self.note_file_suffix}")
            with open(note_file, "wb") as f:
                f.write(note.content)

            if self.sync_timestamp is None \
                    or self.sync_timestamp < max(note.creation_time, note.modification_time):
                self.sync_timestamp = max(note.creation_time, note.modification_time)

            self.last_update_timestamp = datetime.now()

    def dump_image(self, image):
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
                    "creation_time": timestamp_to_str(image.creation_time),
                    "modification_time": timestamp_to_str(image.modification_time)
                }, ensure_ascii=False) + "\n")

            img_file = os.path.join(self.work_dir, f"{image.id}-{self.sync_version}{self.image_file_suffix}")
            with open(img_file, "wb") as f:
                f.write(image.image)

        if self.sync_timestamp is None \
                or self.sync_timestamp < max(image.creation_time, image.modification_time):
            self.sync_timestamp = max(image.creation_time, image.modification_time)

        self.last_update_timestamp = datetime.now()

    def load_change_record(self):
        assert self.request_push() == False, "必须应用完所有已知变更日志才可以Push变更日志"
        start_file_no = (self.sync_version // self.max_file_record_count) * self.max_file_record_count
        end_file_no = (self.max_sync_version // self.max_file_record_count + 1) * self.max_file_record_count

        for file_no in range(start_file_no, end_file_no, self.max_file_record_count):
            change_record_file = f"{self.change_record_prefix}.{file_no}"
            with open(change_record_file, "r") as f:
                for line in f.readlines():
                    record = json.loads(line)
                    if int(record.get("version")) > self.sync_version:
                        record["creation_time"] = timestamp_from_str(record["creation_time"])
                        record["modification_time"] = timestamp_from_str(record["modification_time"])
                        yield record

    def load_note(self, note_id, version):
        note_file = os.path.join(self.work_dir, f"{note_id}-{version}{self.note_file_suffix}")
        count = 1
        while not os.path.exists(note_file):
            time.sleep(0.5)
            count += 1
            if count > 30: raise FileNotFoundError(note_file)

        with open(note_file, "rb") as f:
            content = f.read()
        self.sync_version = version
        self.sync_timestamp = datetime.now()
        return content


    def load_image(self, image_id, version):
        image_file = os.path.join(self.work_dir, f"{image_id}-{version}{self.image_file_suffix}")
        count = 1
        while not os.path.exists(image_file):
            time.sleep(0.5)
            count += 1
            if count > 300: raise FileNotFoundError(image_file)

        with open(image_file, "rb") as f:
            content = f.read()
        self.sync_version = version
        self.sync_timestamp = datetime.now()
        return content

    def request_push(self):
        """
        1. Push锁内部条件：self.sync_version == self.max_sync_version，即必须先引用完所有的变更日志
        2. Push锁外部条件: writing_node相同或者last_update_timestamp很久没有变更
        """

        metadata = self.flush_sync_metadata()

        # Push锁内部条件验证
        if self.sync_version < self.max_sync_version:
            return False

        last_update_timestamp = metadata.get("last_update_timestamp")
        # Push锁外部条件验证last_update_timestamp
        if metadata.get("writing_node") == self.node_name or last_update_timestamp is None:
            self._writing_node = self.node_name
            self.last_update_timestamp = datetime.now()
            self.flush_sync_metadata()
            return True

        time.sleep(self.sync_frequence * 3)
        metadata = self.flush_sync_metadata()
        if metadata.get("last_update_timestamp") == last_update_timestamp:
            self._writing_node = self.node_name
            self.last_update_timestamp = datetime.now()
            self.flush_sync_metadata()
            return True

        return False

    def cleanup_expired_note(self):
        metadata = self.flush_sync_metadata()
        min_version = min(metadata.get("sync_version").values())
        min_version = (min_version // self.max_file_record_count) * self.max_file_record_count

        if self.request_push():
            for filename in os.listdir(self.work_dir):
                if filename == os.path.basename(self.sync_metadata_file):
                    continue
                prefix, subffix = filename.split(".")
                if prefix.startswith(os.path.basename(self.change_record_prefix)):
                    if int(subffix) < min_version:
                        os.remove(os.path.join(self.work_dir, filename))
                else:
                    xid, version = prefix.split("-")
                    if int(version) < min_version:
                        os.remove(os.path.join(self.work_dir, filename))
