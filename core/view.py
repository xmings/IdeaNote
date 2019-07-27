#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2019/5/16
# @Brief: 简述报表功能
from . import core
from flask import render_template, request, Response, jsonify, current_app
from .service import NoteService

note_service = NoteService()

@core.route("/")
def index():
    return render_template('editor.html')


@core.route('/notes',methods=['GET'])
def fetch_notes():
    catalog = note_service.fetch_all_items_to_json()
    return jsonify(catalog)


@core.route('/note/content',methods=['GET'])
def fetch_content():
    item_id = request.args.get('id')
    try:
        content = note_service.read_item_content(item_id)
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=401)
    return content

@core.route('/note/add', methods=['POST'])
def add_note():
    title = request.form.get('title')
    pid = request.form.get('pid')
    try:
        item = note_service.add_item(title, pid)
    except Exception as e:
        current_app.logger.error(e)
        return Response(e, status=401)
    return jsonify({"id": item.id})


@core.route('/note/update/', methods=['POST'])
def update_note():
    id = request.form.get('id')
    type = request.form.get("type")
    try:
        if type == "rename":
            title = request.form.get('title')
            result = note_service.update_item_title(id, title)
        # elif type == "position":
        #     pass
        elif type == "content":
            content = request.form.get('content')
            result = note_service.update_item_content(id, content)
        else:
            raise Exception(f"UNKNOWN PARAMETER: {type}")

        assert result.status, result.content
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=403)

    return 'OK', 200


@core.route('/note/drop', methods=['POST'])
def drop_note():
    id = request.form.get('id')
    try:
        note_service.drop_item(id)
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)
    return Response(status=200)


@core.route('/note/upload/', methods=['POST'])
def upload_image():
    id = request.form.get('id')
    image = request.files.get('image')
    try:
        url_path = note_service.write_item_image(id, image)
    except Exception as e:
        current_app.logger.error(e)
        return "error", 500

    return jsonify({'filename': url_path}), 200

@core.route('/<item_id>/<image_name>')
def download_image(item_id, image_name):
    try:
        image, mime_type = note_service.read_item_image(item_id, image_name)
        assert image and mime_type, "UNKNOWN IMAGE TYPE"
    except Exception as e:
        current_app.logger.error(e)
        return Response(status=403)
    return Response(image, mimetype=mime_type)


@core.route('/sync/<method>', methods=['POST'])
def sync(method):
    if method == 'download':
        status = note_service.note_pull()
    elif method == 'upload':
        status = note_service.note_push()
    else:
        status = note_service.note_sync()
    if not status:
        return Response(status=401)
    return Response(status=200)

