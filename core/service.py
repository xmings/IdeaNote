#!/bin/python
# -*- coding: utf-8 -*-
# @File  : service.py
# @Author: wangms
# @Date  : 2019/8/3
import zlib, requests
from core.model import Catalog, Image, Snap, db
from datetime import datetime
from app import app
from threading import Thread
from sync.weiyun_sync import WeiYunSync
from common import conf
from sqlalchemy import or_


class NoteService(object):
    @classmethod
    def create_note(self, title, parent_id, content, **kwargs):
        content = zlib.compress(content.encode("utf8"))
        last_child = Catalog.query.filter(Catalog.parent_id == parent_id).order_by(Catalog.seq_no.desc()).first()
        seq_no = 1 if not last_child or not last_child.seq_no else last_child.seq_no + 1
        note = Catalog(title=title, parent_id=parent_id, content=content, seq_no=seq_no, **kwargs)
        db.session.add(note)
        db.session.commit()

        return note.id

    @classmethod
    def update_note_title(cls, note_id, title):
        note = Catalog.query.filter_by(id=note_id).first()
        note.title = title
        db.session.commit()
        return True

    @classmethod
    def update_note_position(cls, note_id, prev_note_id=None, parent_id=None):
        assert prev_note_id or parent_id, "either prev_note_id or parent_id is supplied"
        note = Catalog.query.filter_by(id=note_id).first()
        if prev_note_id:
            prev_note = Catalog.query.filter_by(id=prev_note_id).first()
            note.parent_id = prev_note.parent_id
            note.seq_no = prev_note.seq_no + 1
            post_notes = Catalog.query.filter(Catalog.parent_id == prev_note.parent_id,
                                              Catalog.status == 1,
                                              Catalog.seq_no >= prev_note.seq_no,
                                              Catalog.id != note.id,
                                              Catalog.id != prev_note.id).all()
            for n in post_notes:
                n.seq_no = note.seq_no + 2
        else:
            note.parent_id = parent_id
            last_note = Catalog.query.filter_by(parent_id=parent_id).order_by(Catalog.seq_no.desc()).first()
            note.seq_no = 1 if not last_note else last_note.seq_no + 1
        db.session.commit()
        return True

    @classmethod
    def update_note_content(cls, note_id, content):
        note = Catalog.query.filter_by(id=note_id).first()
        # snap = Snap(note_id=note.id, content=note.content)
        # db.session.add(snap)
        note.content = zlib.compress(content.encode("utf8"))
        note.modification_time = datetime.now()
        db.session.commit()
        return True

    @classmethod
    def update_note_status(cls, note_id, status):
        note = Catalog.query.filter_by(id=note_id).first()
        note.status = status
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
                "name": n.title,
                "open": False,
                "parent_id": n.parent_id
            }

        for id, v in notes_dict.items():
            pid = v.get("parent_id")
            if pid and notes_dict.get(pid):
                if not notes_dict[pid].get("children"):
                    notes_dict[pid]["children"] = []
                notes_dict[pid]["children"].append(v)

        root = notes_dict[root.id]
        root["open"] = True
        return root

    @classmethod
    def fetch_note(cls, id):
        note = Catalog.query.filter_by(id=id).first()
        return zlib.decompress(note.content).decode("utf8")

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
    def translate_text(cls, text):
        r = requests.post("http://fy.iciba.com/ajax.php?a=fy", data={"f": "auto", "t": "auto", "w": text})
        return r.json()

    @classmethod
    def sync_notes(cls):
        from sync.github_sync import GithubSync

        # sync = GithubSync()
        # # last_sha is a sha from the latest sync file which is named as `metadata.json`.
        # last_sha = sync.run()
        # rec = SyncRecord(sync_sha=last_sha)
        # db.session.add(rec)
        # # save the last sync sha and each file sha
        # db.session.commit()
        return True

    @classmethod
    def auto_snap(cls):
        import time
        last_time = datetime.now()
        while True:
            time.sleep(60)
            with app.app_context():
                change_notes = Catalog.query.filter(Catalog.modification_time > last_time, Catalog.status == 1).all()
                for n in change_notes:
                    last_snap = Snap.query.filter(Snap.note_id == n.id).order_by(Snap.modification_time.desc()).first()
                    if not last_snap or abs(len(last_snap.content) - len(n.content)) > 100:
                        snap = Snap(note_id=n.id, content=n.content)
                        db.session.add(snap)
                        db.session.commit()
                last_time = datetime.now()

    @classmethod
    def weiyun_auto_sync(cls):
        import time
        wy_sync = WeiYunSync(conf.sync_work_dir)
        while True:
            if wy_sync.request_push():
                with app.app_context():
                    change_note_count = 0
                    for note in Catalog.query.filter(or_(Catalog.creation_time > wy_sync.sync_timestamp,
                                                         Catalog.modification_time > wy_sync.sync_timestamp)).all():
                        wy_sync.dump_note(note)
                        change_note_count += 1
                        for image in Image.query.filter(or_(Catalog.creation_time > wy_sync.sync_timestamp,
                                                            Catalog.modification_time > wy_sync.sync_timestamp),
                                                        Image.note_id == note.id).all():
                            wy_sync.dump_image(image)
                            change_note_count += 1

                if change_note_count == 0:
                    wy_sync.last_update_timestamp = None

                wy_sync.flush_sync_metadata()

            else:
                with app.app_context():
                    for record in wy_sync.load_change_record():
                        version = record.get("version")
                        if record.get("type") == "note":
                            content = wy_sync.load_note(record.get("id"), version)
                            db.session.merge(
                                Catalog(
                                    id=record.get("id"),
                                    title=record.get("title"),
                                    icon=record.get("icon"),
                                    parent_id=record.get("parent_id"),
                                    content=content,
                                    seq_no=record.get("seq_no"),
                                    status=record.get("status"),
                                    creation_time=record.get("creation_time"),
                                    modification_time=record.get("modification_time")
                                )
                            )
                        elif record.get("type") == "image":
                            image = wy_sync.load_image(record.get("id"), version)
                            db.session.merge(
                                Image(
                                    id=record.get("id"),
                                    note_id=record.get("note_id"),
                                    image=image,
                                    mime_type=record.get("mime_type"),
                                    status=record.get("status"),
                                    creation_time=record.get("creation_time"),
                                    modification_time=record.get("modification_time")
                                )
                            )
                    db.session.commit()

                wy_sync.flush_sync_metadata()

            time.sleep(wy_sync.sync_frequence)


at_snap = Thread(target=NoteService.auto_snap)
at_snap.daemon = True
at_snap.start()

weiyun_auto_sync = Thread(target=NoteService.weiyun_auto_sync)
weiyun_auto_sync.daemon = True
weiyun_auto_sync.start()
