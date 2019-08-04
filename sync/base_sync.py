#!/bin/python
# -*- coding: utf-8 -*-
# @File  : base_center.py
# @Author: wangms
# @Date  : 2019/7/27
from core.model import Catalog, SyncRecord, Image, db
from sqlalchemy import or_
import os
import zlib
import json
from uuid import uuid1
from hashlib import sha1
from common import utils
from datetime import datetime


class BaseSync(object):
    def __init__(self):
        self.remote_metadata = {}
        self.metadata_file = utils.conf.metadata_file

    @NotImplemented
    def remote_fetch_note_with_images(self, note_id):
        pass

    @NotImplemented
    def remote_create_note_with_images(self, note_id):
        pass

    @NotImplemented
    def remote_delete_note_with_images(self, note_id):
        pass

    @NotImplemented
    def remote_fetch_metadata(self):
        pass

    @NotImplemented
    def remote_create_or_update_metadata(self):
        pass

    def _auto_complete_path(self, note_id, suffix=".md"):
        path = ''
        note = Catalog.query.filter(Catalog.id == note_id).first()
        while note.id > 1:
            path = f"{note.title}/{path}" if path else note.title
            note = Catalog.query.filter(Catalog.id == note.parent_id).first()

        return f"{path}{suffix}"

    def run(self):
        last_sync = SyncRecord.query.order_by(SyncRecord.creation_time.desc()).first()
        self.local_sha = last_sync.sha
        self.last_sync_time = last_sync.creation_time
        self.remote_metadata = self.remote_fetch_metadata(self.metadata_file)
        if self.remote_metadata["sha"] != self.local_sha:
            self.sync_with_same_verion()
        else:
            self.sync_keep_local_change()

        # 生成metadata
        metadata = {}
        for n in Catalog.query.filter_by(status=1).all():
            metadata[n.id] = {
                "title": n.title,
                "relative_path": self._auto_complete_path(n.id, suffix="md"),
                "img_rel_path_list": {
                    "image_id": ["relative_path", "sha"]
                },
                "status": 1,
                "parent_id": n.parent_id,
                "seq_no": n.seq_no,
                "sha": n.sha,
                "creation_time": str(n.creation_time),
                "modification_time": str(n.modification_time)
            }

        sha = self.remote_update(self.metadata_file,
                                 type="metadata",
                                 sha=self.local_sha,
                                 content=json.dumps(metadata, ensure_ascii=False, indent=4))

        return sha

    def _create_local_change_log(self):
        pass

    def _apply_local_change_log(self):
        pass

    def _create_remote_change_log(self):
        pass

    def _apply_remote_change_log(self):
        pass

    def sync_with_same_verion(self):
        # 同步本地新增
        for n in Catalog.query.filter(Catalog.creation_time > self.last_sync_time,
                                      Catalog.status == 1).all():
            imgs = Image.query.filter(Image.note_id==n.id).all()
            img_dir = self._auto_complete_path(note_id=n.id, suffix='')
            self.remote_metadata[n.id] = {
                "title": n.title,
                "status": 1,
                "parent_id": n.parent_id,
                "seq_no": n.seq_no,
                "images": {
                   i.id: [f"{img_dir}/{i.id}.{i.mime_type.split('/')[1]}"] for i in imgs
                },
                "relative_path": self._auto_complete_path(n.id),
                "creation_time": str(n.creation_time),
                "modification_time": str(n.modification_time)
            }
            self.remote_create_note_with_images(note_id=n.id)

        # 同步本地删除
        for n in Catalog.query.filter(Catalog.creation_time < self.last_sync_time,
                                      Catalog.status == -1).all():
            self.remote_delete_note_with_images(n.id)
            self.remote_metadata.pop(n.id)

        # 同步本地更新
        for n in Catalog.query.filter(Catalog.creation_time < self.last_sync_time,
                                      Catalog.modification_time > self.last_sync_time,
                                      Catalog.status == 1).all():
            # 先删除
            self.remote_delete_note_with_images(n.id)
            self.remote_metadata.pop(n.id)
            # 再创建
            imgs = Image.query.filter(Image.note_id == n.id).all()
            img_dir = self._auto_complete_path(note_id=n.id, suffix='')
            self.remote_metadata[n.id] = {
                "title": n.title,
                "status": 1,
                "parent_id": n.parent_id,
                "seq_no": n.seq_no,
                "images": {
                    i.id: [f"{img_dir}/{i.id}.{i.mime_type.split('/')[1]}"] for i in imgs
                },
                "relative_path": self._auto_complete_path(n.id),
                "creation_time": str(n.creation_time),
                "modification_time": str(n.modification_time)
            }
            self.remote_create_note_with_images(note_id=n.id)

        db.session.commit()

    def sync_keep_local_change(self):
        # 自上一次同步后创建的note不受影响
        # 清楚所有status=-1的note
        # 对比remote_metadata获取并创建不存在的note, 合并自last_sync_time以来被更新的note的信息以及图片
        for note in Catalog.query.filter(Catalog.status == -1).all():
            for img in Image.query.filter(Image.note_id == note.id).all():
                db.session.delete(img)
            db.session.delete(note)

        for id, v in self.remote_metadata.items():
            note = Catalog.query.filter(Catalog.id == id).first()
            if not note:
                note_content = self.remote_fetch_note_with_images(note_id=note.id)
                note = Catalog(id=id,
                               title=v["title"],
                               parent_id=v["parent_id"],
                               content=note_content,
                               seq_no=v["seq_no"],
                               status=1,
                               creation_time=v["creation_time"],
                               modification_time=v["modification_time"])
                db.session.add(note)

                # 创建图片
                for img_id, vv in v["images"].items():
                    img = Image(id=img_id, note_id=note.id, mime_type=f"image/{vv[0].split('.')[1]}")
                    db.session.add(img)

            elif note.modification_time > self.last_sync_time:
                note.title = v["title"]
                note.parent_id = v["parent_id"]
                note.seq_no = v["seq_no"]
                note.creation_time = v["creation_time"]
                note.modification_time = v["modification_time"]
                # 更新图片
                for img_id, vv in v["images"].items():
                    img = Image(id=img_id, note_id=note.id, mime_type=f"image/{vv[0].split('.')[1]}")
                    db.session.add(img)

    def sync_discard_local_change(self):
        # 删除last_sync_time后新建的note
        # 清楚所有status=-1的note
        # 对比remote_metadata获取并创建不存在的note, 还原自last_sync_time以来被更新的note的信息以及图片
        for note in Catalog.query.filter(Catalog.creation_time > self.last_sync_time, Catalog.status == 1).all():
            for img in Image.query.filter(Image.note_id == note.id).all():
                db.session.delete(img)
            db.session.delete(note)

        for note in Catalog.query.filter(Catalog.status == -1).all():
            for img in Image.query.filter(Image.note_id == note.id).all():
                db.session.delete(img)
            db.session.delete(note)

        for id, v in self.remote_metadata.items():
            note = Catalog.query.filter(Catalog.id == id).first()
            if not note:
                note_content = self.remote_fetch_note_with_images(note_id=note.id)
                note = Catalog(id=id,
                               title=v["title"],
                               parent_id=v["parent_id"],
                               content=note_content,
                               seq_no=v["seq_no"],
                               status=1,
                               creation_time=v["creation_time"],
                               modification_time=v["modification_time"])
                db.session.add(note)
            elif note.modification_time > self.last_sync_time:
                note.title = v["title"]
                note.parent_id = v["parent_id"]
                note.seq_no = v["seq_no"]
                note.creation_time = v["creation_time"]
                note.modification_time = v["modification_time"]

        db.session.commit()