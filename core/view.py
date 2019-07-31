#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2019/5/16
# @Brief: 简述报表功能
from . import core
from flask import render_template, request, Response, jsonify, current_app
from core.model import Catalog, Image
from app import db
import mimetypes


@core.route("/")
def index():
    return render_template('editor.html')


@core.route('/notes', methods=['GET'])
def fetch_notes():
    notes = Catalog.query.filter_by(status=1).order_by(Catalog.parent_id, Catalog.seq_no)
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
        notes_dict[v["parent_id"]]["children"].append(v)

    catalog = notes_dict[0]
    catalog["open"] = True
    return jsonify(catalog)


@core.route('/note/content', methods=['GET'])
def fetch_content():
    note_id = request.args.get('id')
    try:
        note = Catalog.query.filter_by(id=int(note_id), status=1).first()
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=401)
    return note.content


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
    note = Catalog.query.filter_by(id=int(id), status=1).first()
    try:
        if type == "rename":
            title = request.form.get('title')
            note.title = title
            db.session.commit()
        # elif type == "position":
        #     pass
        elif type == "content":
            content = request.form.get('content')
            if content == "":
                raise Exception("It's dangerous to clear up a item, think twice please!")
            note.title = content
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
        note = Catalog.query.filter_by(id=int(id), status=1).first()
        note.status = -1
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
        img = Image(note_id=id, image=image)
        db.session.add(img)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return "error", 500

    return jsonify({'filename': f"/{id}/{img.id}"}), 200


@core.route('/<note_id>/<image_name>')
def download_image(note_id, image_name):
    try:
        img = Image.query.filter_by(note_id=note_id, id=image_name)
        assert img , "UNKNOWN IMAGE TYPE"
    except Exception as e:
        current_app.logger.error(e)
        return Response(status=403)
    return Response(img, mimetype="image/png")


@core.route('/sync/<method>', methods=['POST'])
def sync(method):
    return Response(status=200)

