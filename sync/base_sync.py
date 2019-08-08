#!/bin/python
# -*- coding: utf-8 -*-
# @File  : base_center.py
# @Author: wangms
# @Date  : 2019/7/27
from core.model import Catalog, SyncRecord, Image, db
from core.service import NoteService
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
        self.datetime_formatter = "%Y-%m-%d %H:%M:%S.%f"
        self.root_note = Catalog.query.filter(Catalog.parent_id == "self").first()

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

        if Catalog.query.filter(Catalog.parent_id == note_id).all():
            return f"{path}/init.md" if path else "init.md"
        return f"{path}.md"

    def _auto_gen_image_path(self, note_id, image_id):
        dir = os.path.dirname(self._auto_gen_note_path(note_id))
        return f"{dir}/.img/{image_id}" if dir else f".img/{image_id}"

    def _delete_note_with_children(self, note_id):
        note = Catalog.query.filter_by(id=note_id).first()
        delete_notes = [note]
        while delete_notes:
            note = delete_notes.pop(0)
            children = Catalog.query.filter_by(parent_id=note.id).all()
            delete_notes += list(children)

            if note.modification_time < self.local_last_sync_time:
                db.session.delete(note)
            else:
                note.parent_id = self.root_note
                note.seq_no = 10000

        db.session.commit()
        return True

    def run(self):
        self.remote_metadata, self.remote_metadata_sha = self.fetch_metadata_and_sha()
        if not self.remote_metadata:
            return self.init_sync()

        self.local_last_sync_sha = self.last_sync.sync_sha if self.last_sync else None
        self.local_last_sync_time = self.last_sync.creation_time if self.last_sync else datetime(year=1990, month=1,
                                                                                                 day=1)

        if self.remote_metadata_sha == self.local_last_sync_sha:
            status = 0
            try:
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
                        for img in Image.query.filter(Image.note_id == n.id).all():
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
                    try:
                        self.delete_remote_note(n.id)
                        for img_id in self.remote_metadata[n.id]["images"].keys():
                            self.delete_remote_image(n.id, img_id)
                        self.remote_metadata.pop(n.id)
                    except KeyError:
                        pass
            except Exception as e:
                status = -1
                print(e)
            finally:
                # 更新remote-metadata
                self.update_metadata()

            if status == 0:
                # 创建同步记录
                record = SyncRecord(sync_sha=self.remote_metadata_sha)
                db.session.add(record)
                db.session.commit()

        else:
            # 本地新增的先把状态置为-11
            Catalog.query.filter(Catalog.creation_time > self.local_last_sync_time,
                                 Catalog.status == 1).update({Catalog.status: -11})

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

            # 同步远程到本地(新增的就创建本地note、属性不一致就覆盖（除了content）、不存在就删除本地对应note)
            for id, v in self.remote_metadata.items():
                note = Catalog.query(Catalog.id).filter(Catalog.status == 1, Catalog.id == id).first()
                if not note:
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
                else:
                    # 合并远程和本地更新, 放弃本地的parent_id、title、seq_no的修改，本地内容发生变更的先把状态置为-12
                    if not self.is_note_content_equal(id, note.content):
                        note.remote_content = zlib.compress(self.fetch_remote_note(id))
                        note.status = -12
                        for img_id, v in self.remote_metadata[note.id]["images"].items():
                            if not Image.filter(Image.note_id == note.id).first():
                                image = Image(
                                    id=img_id,
                                    note_id=note.id,
                                    image=zlib.compress(self.fetch_remote_image(note.id, img_id)),
                                    mime_type=v["mime_type"],
                                    status=1,
                                    creation_time=datetime.now()
                                )
                                db.session.add(image)
                    note.title = v["title"]
                    note.parent_id = v["parent_id"]
                    note.seq_no = v["seq_no"]
                    note.creation_time = datetime.strptime(v["creation_time"], self.datetime_formatter)
                    note.modification_time = datetime.strptime(v["modification_time"], self.datetime_formatter)

            # 删除远程已不存在的且上一次同步以来未发生变化的note，发生变化的note直接移动到root目录下
            for n in Catalog.query(Catalog.id).filter(Catalog.status == 1).all():
                if n.creation_time < self.local_last_sync_time and \
                        n.id not in self.remote_metadata:
                    self._delete_note_with_children(n.id)

            # 创建同步记录
            record = SyncRecord(sync_sha=self.remote_metadata_sha)
            db.session.add(record)

            Catalog.query.filter(Catalog.status == -11).update({Catalog.status: 1, Catalog.creation_time: datetime.now()})
            Catalog.query.filter(Catalog.status == -12).update({Catalog.status: 1, Catalog.modification_time: datetime.now()})
            db.session.commit()

    def init_sync(self):
        for n in Catalog.query.filter(Catalog.status == 1).all():
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

            for img in Image.query.filter(Image.note_id == n.id).all():
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
