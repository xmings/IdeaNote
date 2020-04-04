#!/bin/python
# -*- coding: utf-8 -*-
# @File  : service.py
# @Author: wangms
# @Date  : 2019/8/3
import zlib, requests
from core.model import Catalog, Image, db
from datetime import datetime
from app import app
from flask import session
from sqlalchemy.sql import functions
from common import SyncStatusEnum, NoteStatusEnum, PasswordStatusEnum

class NoteService(object):
    catalog_root_id = 0
    @classmethod
    def create_note(self, title, parent_id, content, **kwargs):
        content = zlib.compress(content.encode("utf8"))
        last_child = Catalog.query.filter(Catalog.parent_id == parent_id).order_by(Catalog.seq_no.asc()).first()
        seq_no = 1 if not last_child or not last_child.seq_no else last_child.seq_no + 1
        note = Catalog(title=title, parent_id=parent_id, content=content, seq_no=seq_no, **kwargs)
        note.status = NoteStatusEnum.create.value
        note.sync_status = SyncStatusEnum.need_sync.value
        db.session.add(note)
        db.session.commit()

        return note.id

    @classmethod
    def update_note_title(cls, note_id, title):
        note = Catalog.query.filter_by(id=note_id).first()
        note.title = title
        note.sync_status = SyncStatusEnum.need_sync.value
        note.modification_time = datetime.now()
        note.status = NoteStatusEnum.update_title.value
        db.session.commit()
        return True

    @classmethod
    def update_note_position(cls, note_id, parent_id, index):
        note = Catalog.query.filter_by(id=note_id).first()
        node_seq = 0
        for child in Catalog.query.filter(
                Catalog.parent_id==parent_id,
                Catalog.status != NoteStatusEnum.delete.value,
                Catalog.id!=note.id
        ).order_by(Catalog.seq_no.asc()).all():
            if node_seq == index:
                # 为note留出该位置
                node_seq += 1
            if child.seq_no != node_seq:
                child.seq_no = node_seq
                child.sync_status = SyncStatusEnum.need_sync.value
                child.modification_time = datetime.now()
                child.status = NoteStatusEnum.update_position.value

            node_seq += 1
        # 最后插入该位置
        note.parent_id = parent_id
        note.seq_no = index
        note.sync_status = SyncStatusEnum.need_sync.value
        note.modification_time = datetime.now()
        note.status = NoteStatusEnum.update_position.value
        db.session.commit()
        return True

    @classmethod
    def update_note_content(cls, note_id, content):
        note = Catalog.query.filter_by(id=note_id).first()
        if zlib.decompress(note.content).decode("utf8") == content:
            return True
        note.content = zlib.compress(content.encode("utf8"))
        note.sync_status = SyncStatusEnum.need_sync.value
        note.modification_time = datetime.now()
        note.status = NoteStatusEnum.update_content.value
        db.session.commit()
        return True

    @classmethod
    def update_note_lock_status(cls, note_id, toggle=True, lock=True):
        note = Catalog.query.filter_by(id=note_id).first()
        if toggle:
            note.with_passwd = PasswordStatusEnum.has_password.value \
                if note.with_passwd == PasswordStatusEnum.no_password.value else PasswordStatusEnum.no_password.value
        else:
            note.with_passwd = PasswordStatusEnum.has_password.value if lock else PasswordStatusEnum.no_password.value
        note.sync_status = SyncStatusEnum.need_sync.value
        note.modification_time = datetime.now()
        note.status = NoteStatusEnum.update_lock.value
        db.session.commit()
        return True

    @classmethod
    def delete_note(cls, id):
        note = Catalog.query.filter_by(id=id).first()
        delete_notes = [note]
        while delete_notes:
            note = delete_notes.pop(0)
            children = Catalog.query.filter_by(parent_id=note.id).all()
            delete_notes += list(children)

            note.sync_status = SyncStatusEnum.need_sync.value
            note.status = NoteStatusEnum.delete.value
            note.modification_time = datetime.now()

        db.session.commit()
        return True

    @classmethod
    def fetch_catalog_tree(cls):
        root = Catalog.query.filter(Catalog.status != NoteStatusEnum.delete.value, Catalog.parent_id == "self").first()
        notes = Catalog.query.filter(Catalog.status != NoteStatusEnum.delete.value).order_by(Catalog.parent_id, Catalog.seq_no).all()
        notes_dict = {}
        for n in notes:
            notes_dict[n.id] = {
                "id": n.id,
                "text": n.title,
                "type": "file",
                "parent_id": n.parent_id
            }

        for id, v in notes_dict.items():
            pid = v.get("parent_id")
            if pid and notes_dict.get(pid):
                if not notes_dict[pid].get("children"):
                    notes_dict[pid]["children"] = []
                notes_dict[pid]["children"].append(v)
                notes_dict[pid]["type"] = "folder"

        cls.catalog_root_id = root.id
        root = notes_dict[root.id]
        root["opened"] = True
        return root

    @classmethod
    def need_auth_code(cls, id):
        note = Catalog.query.filter_by(id=id).first()
        with app.app_context():
            if note.with_passwd == 0:
                return False
            else:
                if f"auth-{id}" in session:
                    return False
        return True

    @classmethod
    def fetch_note(cls, id):
        note = Catalog.query.filter_by(id=id).first()
        content = zlib.decompress(note.content).decode("utf8")
        images = Image.query.filter(Image.note_id == id, Image.status != NoteStatusEnum.delete.value).all()
        for img in images:
            if img.id not in content:
                img.status = NoteStatusEnum.delete.value
                img.modification_time = datetime.now()
                db.session.commit()
        return content

    @classmethod
    def fetch_recently_change_note(cls):
        notes = Catalog.query.order_by(
            functions.coalesce(Catalog.creation_time, Catalog.modification_time).desc()).limit(30).all()
        notes_list = []
        status_text_mapping = {
            NoteStatusEnum.create.value: "新建笔记",
            NoteStatusEnum.update_title.value: "更新标题",
            NoteStatusEnum.update_content.value: "更新内容",
            NoteStatusEnum.update_lock.value: "更新密码",
            NoteStatusEnum.update_position.value: "更新顺序",
            NoteStatusEnum.delete.value: "删除笔记"
        }
        for n in notes:
            notes_list.append({
                "id": n.id,
                "title": n.title,
                "status": status_text_mapping[n.status],
                "sync_status": "已同步" if n.sync_status == SyncStatusEnum.has_sync.value else "未同步",
                "change_time": str(n.modification_time if n.modification_time else n.creation_time)
            })

        return notes_list

    @classmethod
    def create_image(cls, note_id, image, image_id=None):
        image_content = zlib.compress(image.read())
        image = Image(id=image_id, note_id=note_id, image=image_content, mime_type=image.mimetype)
        image.status = NoteStatusEnum.create
        db.session.add(image)
        db.session.commit()
        return image.id

    @classmethod
    def fetch_image(cls, image_id):
        img = Image.query.filter_by(id=image_id).first()
        return zlib.decompress(img.image), img.mime_type

    @classmethod
    def fetch_images(cls, note_id):
        imgs = Image.query.filter_by(note_id=note_id).all()
        return ((zlib.decompress(i.image), i.mime_type) for i in imgs)

    @classmethod
    def translate_text(cls, text):
        r = requests.post("http://fy.iciba.com/ajax.php?a=fy", data={"f": "auto", "t": "auto", "w": text})
        return r.json()
