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


class NoteService(object):
    @classmethod
    def create_note(self, title, parent_id, content, **kwargs):
        content = zlib.compress(content.encode("utf8"))
        last_child = Catalog.query.filter(Catalog.parent_id == parent_id).order_by(Catalog.seq_no.asc()).first()
        seq_no = 1 if not last_child or not last_child.seq_no else last_child.seq_no + 1
        note = Catalog(title=title, parent_id=parent_id, content=content, seq_no=seq_no, **kwargs)
        note.sync_status = 2
        db.session.add(note)
        db.session.commit()

        return note.id

    @classmethod
    def update_note_title(cls, note_id, title):
        note = Catalog.query.filter_by(id=note_id).first()
        note.title = title
        note.sync_status = 2
        note.modification_time = datetime.now()
        db.session.commit()
        return True

    @classmethod
    def update_note_position(cls, note_id, parent_id, index):
        note = Catalog.query.filter_by(id=note_id).first()
        node_seq = 0
        for child in Catalog.query.filter(
                Catalog.parent_id==parent_id,
                Catalog.status != -1,
                Catalog.id!=note.id
        ).order_by(Catalog.seq_no.asc()).all():
            if node_seq == index:
                # 为note留出该位置
                node_seq += 1

            child.seq_no = node_seq
            child.status = 3
            child.sync_status = 2
            child.modification_time = datetime.now()
            node_seq += 1
        # 最后插入该位置
        note.parent_id = parent_id
        note.seq_no = index
        note.sync_status = 2
        note.modification_time = datetime.now()

        db.session.commit()
        return True

    @classmethod
    def update_note_content(cls, note_id, content):
        note = Catalog.query.filter_by(id=note_id).first()
        if zlib.decompress(note.content).decode("utf8") == content:
            return True
        note.content = zlib.compress(content.encode("utf8"))
        note.sync_status = 2
        note.modification_time = datetime.now()
        db.session.commit()
        return True

    @classmethod
    def update_note_status(cls, note_id, status):
        note = Catalog.query.filter_by(id=note_id).first()
        note.status = status
        note.sync_status = 2
        note.modification_time = datetime.now()
        db.session.commit()
        return True

    @classmethod
    def update_note_lock_status(cls, note_id, toggle=True, lock=True):
        note = Catalog.query.filter_by(id=note_id).first()
        if toggle:
            note.with_passwd = 1 if note.with_passwd == 0 else 0
        else:
            note.with_passwd = 1 if lock else 0
        note.sync_status = 2
        note.modification_time = datetime.now()
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

            note.status = -1
            note.sync_status = 2
            note.modification_time = datetime.now()

        db.session.commit()
        return True

    @classmethod
    def fetch_catalog_tree(cls):
        root = Catalog.query.filter(Catalog.status != -1, Catalog.parent_id == "self").first()
        notes = Catalog.query.filter(Catalog.status != -1).order_by(Catalog.parent_id, Catalog.seq_no).all()
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
        images = Image.query.filter(Image.note_id==id, Image.status != -1).all()
        for img in images:
            if img.id not in content:
                img.status = -1
                img.modification_time = datetime.now()
                db.session.commit()
        return content

    @classmethod
    def create_image(cls, note_id, image, image_id=None):
        image_content = zlib.compress(image.read())
        image = Image(id=image_id, note_id=note_id, image=image_content, mime_type=image.mimetype)
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
    def fetch_need_merge_notes(cls):
        notes = Catalog.query.filter(Catalog.status==2).all()
        return notes

    @classmethod
    def translate_text(cls, text):
        r = requests.post("http://fy.iciba.com/ajax.php?a=fy", data={"f": "auto", "t": "auto", "w": text})
        return r.json()
