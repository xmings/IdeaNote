#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2019/5/16
# @Brief: 简述报表功能
from . import core
from flask import render_template, request, Response, jsonify, current_app
from core.model import Catalog, Image, Snap, SyncRecord
from app import db
import zlib
from datetime import datetime
# from sync.github_sync import GithubSync

@core.route("/")
def index():
    return render_template('editor.html')


@core.route('/notes', methods=['GET'])
def fetch_notes():
    root = Catalog.query.filter(Catalog.status!=-1, Catalog.parent_id=="self").first()
    notes = Catalog.query.filter(Catalog.status!=-1).order_by(Catalog.parent_id, Catalog.seq_no).all()
    notes_dict = {}
    for n in notes:
        notes_dict[n.id] = {
            "id": n.id,
            "name": n.title,
            "open": False,
            "children": [],
            "parent_id": n.parent_id
        }

    for id, v in notes_dict.items():
        pid = v.get("parent_id")
        if pid and notes_dict.get(pid):
            notes_dict[pid]["children"].append(v)

    root = notes_dict[root.id]
    root["open"] = True
    return jsonify(root)


@core.route('/note/content', methods=['GET'])
def fetch_content():
    note_id = request.args.get('id')
    try:
        note = Catalog.query.filter_by(id=note_id, status=1).first()
        content = zlib.decompress(note.content).decode("utf8")
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=401)
    return content


@core.route('/note/add', methods=['POST'])
def add_note():
    title = request.form.get('title')
    pid = request.form.get('pid')
    try:
        note = Catalog(title=title, parent_id=pid)
        db.session.add(note)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return Response(e, status=401)
    return jsonify({"id": note.id})


@core.route('/note/update/', methods=['POST'])
def update_note():
    id = request.form.get('id')
    type = request.form.get("type")
    note = Catalog.query.filter_by(id=id, status=1).first()
    try:
        if type == "rename":
            title = request.form.get('title')
            note.title = title
            note.modification_time = datetime.now()
            db.session.commit()
        elif type == "position":
            prev_note_id = request.form.get('prev_note_id')
            prev_note = Catalog.query.filter_by(id=prev_note_id, status=1).first()
            note.parent_id = prev_note.parent_id
            note.seq_no = prev_note.seq_no + 1
            post_notes = Catalog.query.filter(Catalog.parent_id==prev_note.parent_id,
                                              Catalog.status==1,
                                              Catalog.seq_no>prev_note.seq_no,
                                              Catalog.id != note.id).all()
            for n in post_notes:
                n.seq_no = note.seq_no + 1
            db.session.commit()
        elif type == "content":
            content = request.form.get('content')
            if content == "" and len(note.content) > 100:
                raise Exception("It's dangerous to clear up a item, think twice please!")

            snap = Snap(note_id=note.id, content=note.content)
            db.session.add(snap)
            note.content = zlib.compress(content.encode("utf8"))
            note.modification_time = datetime.now()
            db.session.commit()
        else:
            raise Exception(f"UNKNOWN PARAMETER: {type}")

    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=403)

    return 'OK', 200


@core.route('/note/drop', methods=['POST'])
def drop_note():
    id = request.form.get('id')
    try:
        note = Catalog.query.filter_by(id=id, status=1).first()
        note.status = -1
        note.modification_time = datetime.now()
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)
    return Response(status=200)


@core.route('/note/upload/', methods=['POST'])
def upload_image():
    id = request.form.get('id')
    image = request.files.get('image')
    try:
        image_content = zlib.compress(image.read())
        img = Image(note_id=id, image=image_content, mime_type=image.mimetype)
        db.session.add(img)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return "error", 500

    return jsonify({'filename': f"/{id}/{img.id}"}), 200


@core.route('/<note_id>/<image_name>')
def download_image(note_id, image_name):
    try:
        img = Image.query.filter_by(note_id=note_id, id=image_name).first()
        image_content = zlib.decompress(img.image)
        assert image_content , "UNKNOWN IMAGE TYPE"
    except Exception as e:
        current_app.logger.error(e)
        return Response(status=403)
    return Response(image_content, mimetype=img.mime_type)


@core.route("/sync", methods=["GET"])
def sync_note():
    # sync = GithubSync()
    # # last_sha is a sha from the latest sync file which is named as `metadata.json`.
    # last_sha = sync.run()
    #
    # rec = SyncRecord(sync_sha=last_sha)
    # db.session.add(rec)
    # # save the last sync sha and each file sha
    # db.session.commit()

    # 生成metadata
    # metadata = {}
    # for n in Catalog.query.filter_by(status=1).all():
    #     metadata[n.id] = {
    #         "title": n.title,
    #         "relative_path": self._auto_complete_path(n.id),
    #         "img_rel_path_list": [],
    #         "status": 1,
    #         "parent_id": n.parent_id,
    #         "seq_no": n.seq_no,
    #         "sha": n.sha,
    #         "creation_time": str(n.creation_time),
    #         "modification_time": str(n.modification_time)
    #     }
    #
    # self.remote_update(self.metadata_file,
    #                    json.dumps(metadata, ensure_ascii=False, indent=4))


    return Response(status=200)