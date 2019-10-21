#!/bin/python
# -*- coding: utf-8 -*-
# @File  : weiyun_sync.py
# @Author: wangms
# @Date  : 2019/8/8
# @Brief: 简述报表功能
import json
import os
import socket
from datetime import datetime, timedelta
import sqlalchemy

class WeiYunSync(object):
    def __init__(self, work_dir):
        self.change_log = []
        self.work_dir = work_dir
        self.change_log_file = os.path.join(self.work_dir, "change.rec")
        self.sync_metadata_file = os.path.join(self.work_dir, "sync.metadata")

    def cleanup_work_dir(self):
        if self.can_upload():
            os.removedirs(self.work_dir)

    def dump_note(self, note):
        self.change_log.append({
            "type": "note",
            "id": note.id,
            "title": note.title,
            "icon": note.icon,
            "parent_id": note.parent_id,
            "seq_no": note.seq_no,
            "status": note.status,
            "creation_time": str(note.creation_time),
            "modification_time": str(note.modification_time)
        })
        note_file = os.path.join(self.work_dir, f"{note.id}.note")
        with open(note_file, "wb") as f:
            f.write(note.content)

        with open(self.change_log_file, "a+") as f:
            f.write(json.dumps(self.change_log[-1]))

        with open(self.sync_metadata_file, "w") as f:
            f.write(json.dumps({
                "host": socket.gethostname(),
                "last_sync_time": str(datetime.now())
            }))

    def dump_images(self, image):
        self.change_log.append({
            "type": "image",
            "id": image.id,
            "note_id": image.note_id,
            "mime_type": image.mime_type,
            "status": image.status,
            "creation_time": image.creation_time,
            "modification_time": image.modification_time
        })
        img_file = os.path.join(self.work_dir, f"{image.id}.img")
        with open(img_file, "wb") as f:
            f.write(image.image)

        with open(self.change_log_file, "a+") as f:
            f.write(json.dumps(self.change_log[-1]))

    def apply_change_log(self):
        assert self.change_log == []
        # 获取change_log_file的md5，以待加载完成后判断是否清理掉该目录下的所有文件


    def _load_note(self):
        pass

    def _load_image(self):
        pass

    def can_upload(self):
        if not os.path.exists(self.change_log_file):
            return True

        with open(self.change_log_file, "r") as f:
            sync_metadata = json.loads(f.read())

        if not sync_metadata:
            return True

        last_sync_time = datetime.fromisoformat(sync_metadata.get("last_sync_time"))
        if sync_metadata.get("host") == socket.gethostname():
            return True
        elif last_sync_time < datetime.now() - timedelta(seconds=60):
            return True
        return False







