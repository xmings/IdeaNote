#!/bin/python
# -*- coding: utf-8 -*-
# @File  : base_center.py
# @Author: wangms
# @Date  : 2019/7/27
from core.model import Catalog, SyncRecord, Image, db
import zlib
import os
from hashlib import sha1
from common import utils
from datetime import datetime


class BaseSync(object):
    def __init__(self):
        self.remote_metadata = {}
        self.remote_metadata_sha = None
        self.metadata_file = utils.conf.metadata_file
        self.last_sync = SyncRecord.query.order_by(SyncRecord.creation_time.desc()).first()

    def is_note_content_equal(self, note_id, local_content):
        remote_sha = self.remote_metadata[note_id]["sha"]
        local_content = zlib.decompress(local_content)
        local_sha = b"blob " + str(len(local_content)).encode() + b"\0" + local_content
        s1 = sha1()
        s1.update(local_sha)
        return s1.hexdigest() == remote_sha

    def _auto_gen_note_path(self, note_id):
        path = ''
        note = Catalog.query.filter(Catalog.id == note_id).first()
        while note.parent_id != "self":
            path = f"{note.title}/{path}" if path else note.title
            note = Catalog.query.filter(Catalog.id == note.parent_id).first()

        if Catalog.query.filter(Catalog.parent_id==note_id).all():
            return f"{path}/init.md" if path else "init.md"
        return f"{path}.md"

    def _auto_gen_image_path(self, note_id, image_id):
        dir = os.path.dirname(self._auto_gen_note_path(note_id))
        return  f"{dir}/.img/{image_id}" if dir else f".img/{image_id}"

    def run(self):
        self.remote_metadata, self.remote_metadata_sha = self.fetch_metadata_and_sha()
        if not self.remote_metadata:
            return self.init_sync()

        self.local_last_sync_sha = self.last_sync.sync_sha if self.last_sync else None
        self.local_last_sync_time = self.last_sync.creation_time if self.last_sync else datetime(year=1990,month=1,day=1)

        if self.remote_metadata_sha == self.local_last_sync_sha:
            # put-create
            local_create = Catalog.query.filter(Catalog.creation_time > self.local_last_sync_time,
                                                Catalog.status == 1).all()
            for n in local_create:
                self.remote_metadata[n.id] = {
                    "title": n.title,
                    "images": {},
                    "status": 1,
                    "parent_id": n.parent_id,
                    "seq_no": n.seq_no,
                    "creation_time": str(n.creation_time),
                    "modification_time": str(n.modification_time)
                }
                self.create_remote_note(n.id, zlib.decompress(n.content))

                images = Image.query.filter(Image.query.filter(Image.note_id == n.id)).all()
                for img in images:
                    self.remote_metadata[n.id]["images"][img.id] = {
                        "mime_type": img.mime_type
                    }
                    self.create_remote_image(n.id, img.id, zlib.compress(img.image))

            # put-update
            local_update = Catalog.query.filter(Catalog.creation_time < self.local_last_sync_time,
                                                Catalog.modification_time > self.local_last_sync_time,
                                                Catalog.status == 1).all()
            for n in local_update:
                if n.parent_id != self.remote_metadata[n.id]["parent_id"] or \
                        n.title != self.remote_metadata[n.id]["title"]:
                    self.delete_remote_note(n.id)
                    for img_id in self.remote_metadata[n.id]["images"]:
                        self.delete_remote_image(n.id, img_id)

                    self.remote_metadata[n.id] = {
                        "title": n.title,
                        "images": {},
                        "status": 1,
                        "parent_id": n.parent_id,
                        "seq_no": n.seq_no,
                        "creation_time": str(n.creation_time),
                        "modification_time": str(n.modification_time)
                    }
                    self.create_remote_note(n.id, zlib.decompress(n.content))

                    images = Image.query.filter(Image.query.filter(Image.note_id == n.id)).all()
                    for img in images:
                        self.remote_metadata[n.id]["images"][img.id] = {
                            "mime_type": img.mime_type
                        }
                        self.create_remote_image(n.id, img.id, zlib.compress(img.image))

                elif not self.is_note_content_equal(n.id, n.content):
                    self.update_remote_note(n.id, zlib.decompress(n.content))
                    images = Image.query.filter(Image.query.filter(Image.note_id == n.id)).all()
                    for img in images:
                        if img.id not in self.remote_metadata[n.id]["images"].keys():
                            self.remote_metadata[n.id]["images"][img.id] = {
                                "mime_type": img.mime_type
                            }
                            self.create_remote_image(n.id, img.id, zlib.compress(img.image))

                self.remote_metadata["seq_no"] = str(n.seq_no)
                self.remote_metadata["creation_time"] = str(n.creation_time)
                self.remote_metadata["modification_time"] = str(n.modification_time)
                self.remote_metadata["seq_no"] = str(n.seq_no)

            # put-delete
            local_delete = Catalog.query.filter(Catalog.creation_time < self.local_last_sync_time,
                                                Catalog.modification_time > self.local_last_sync_time,
                                                Catalog.status == -1).all()
            for n in local_delete:
                self.delete_remote_note(n.id)
                for img_id in self.remote_metadata[n.id]["images"].keys():
                    self.delete_remote_image(n.id, img_id)
                self.remote_metadata.pop(n.id)

            # 更新remote-metadata
            self.update_metadata()

            # 创建同步记录
            record = SyncRecord(sync_sha=self.remote_metadata_sha)
            db.session.add(record)
            db.session.commit()

        else:
            # 先同步remote到本地，再应用本地变更（只应用update和create，delete）
            local_create = Catalog.query.filter(Catalog.creation_time > self.local_last_sync_time,
                                                Catalog.status == 1).all()

            local_update = Catalog.query.filter(Catalog.creation_time < self.local_last_sync_time,
                                                Catalog.modification_time > self.local_last_sync_time,
                                                Catalog.status == 1).all()

            local_delete = Catalog.query.filter(Catalog.status == -1).all()
            # 清理自上一次同步以来的新创建再删除的note, 放弃上一次同步之前存在同步之后的删除
            for n in local_delete:
                if n.creation_time > self.local_last_sync_time or \
                        n.modification_time < self.local_last_sync_time:
                    db.session.delete(n)
                    Image.query.filter(Image.note_id == n.id).delete()
                else:
                    n.status = 1
            db.session.commit()

            local_unchange_ids = Catalog.query(Catalog.id).filter(Catalog.status == 1).all()
            remote_new_notes = filter(lambda x: x.id not in local_unchange_ids, self.remote_metadata)

            # 同步远程新增到本地
            for id in remote_new_notes:
                v = self.remote_metadata[id]
                content = self.fetch_remote_note(id)
                note = Catalog(
                    id=id,
                    title=v["title"],
                    parent_id=v["parent_id"],
                    content=zlib.compress(content),
                    seq_no=v["seq_no"],
                    status=1,
                    creation_time=v["creation_time"],
                    modification_time=v["modification_time"]
                )
                db.session.add(note)
                for img_id, v in self.remote_metadata[id]["images"].items():
                    image = Image(
                        id=img_id,
                        note_id=id,
                        image=zlib.compress(self.fetch_remote_image(id, img_id)),
                        mime_type=v["mime_type"],
                        status=1,
                        creation_time=datetime.now()
                    )

                    db.session.add(image)

            # 创建同步记录
            record = SyncRecord(sync_sha=self.remote_metadata_sha)
            db.session.add(record)
            db.session.commit()

            # 合并远程和本地更新, 放弃本地的parent_id、title、seq_no的修改
            for n in local_update:
                v = self.remote_metadata[n.id]
                if not self.is_note_content_equal(n.id, n.content):
                    remote_content = self.fetch_remote_note(v["relative_path"])
                    n.remote_content = zlib.compress(remote_content)
                    n.creation_time = datetime.now()
                    n.modification_time = None
                    note_image_ids = Image.query(Image.id).filter(Image.note_id == n.id).all()
                    for img_id, v in self.remote_metadata[n.id]["images"].items():
                        if img_id not in note_image_ids:
                            image = Image(
                                id=img_id,
                                note_id=n.id,
                                image=zlib.compress(self.fetch_remote_image(n.id, img_id)),
                                mime_type=v["mime_type"],
                                status=1,
                                creation_time=datetime.now()
                            )
                            db.session.add(image)

                n.title = v["title"]
                n.parent_id = v["parent_id"]
                n.seq_no = v["seq_no"]

            # 修改local_create的create_time=now()
            for n in local_create:
                n.creation_time = datetime.now()
                n.modification_time = None

            db.session.commit()

    def init_sync(self):
        for n in Catalog.query.filter(Catalog.status==1).all():
            self.remote_metadata[n.id] = {
                "title": n.title,
                "images": {},
                "status": 1,
                "parent_id": n.parent_id,
                "seq_no": n.seq_no,
                "creation_time": str(n.creation_time),
                "modification_time": str(n.modification_time)
            }
            self.create_remote_note(n.id, zlib.decompress(n.content))

            for img in Image.query.filter(Image.note_id==n.id).all():
                self.remote_metadata[n.id]["images"][img.id] = {
                    "mime_type": img.mime_type
                }
                self.create_remote_image(n.id, img.id, zlib.decompress(img.image))

        self.update_metadata()

        # 创建同步记录
        record = SyncRecord(sync_sha=self.remote_metadata_sha)
        db.session.add(record)
        db.session.commit()

    def fetch_metadata_and_sha(self):
        raise NotImplementedError

    def update_metadata(self):
        raise NotImplementedError

    def fetch_remote_note(self, note_id):
        raise NotImplementedError

    def create_remote_note(self, note_id, content):
        raise NotImplementedError

    def update_remote_note(self, note_id, content):
        raise NotImplementedError

    def delete_remote_note(self, note_id):
        raise NotImplementedError

    def fetch_remote_image(self, note_id, image_id):
        raise NotImplementedError

    def create_remote_image(self, note_id, image_id, content):
        raise NotImplementedError

    def update_remote_image(self, note_id, image_id, content):
        raise NotImplementedError

    def delete_remote_image(self, note_id, image_id):
        raise NotImplementedError
