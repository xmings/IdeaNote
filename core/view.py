#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2019/5/16
# @Brief: 简述报表功能
from . import core
from flask import render_template, request, Response, jsonify, current_app, session
from core.service import NoteService
from common import conf

@core.route("/")
def index():
    for i in [ii for ii in session if ii.startswith('auth')]:
        session.pop(i)
    return render_template('editor.html')

@core.route("/note/auth", methods=["POST"])
def auth():
    note_id = request.form.get('id')
    auth_code = request.form.get('auth_code')
    if auth_code != str(conf.auth_code):
        return Response(status=400)

    session[f"auth-{note_id}"] = 1
    return Response(status=200)

@core.route("/note/toggle/lock", methods=["POST"])
def toggle_note_lock():
    note_id = request.form.get('id')
    try:
        if NoteService.need_auth_code(note_id):
            return Response(status=401)
        NoteService.update_note_lock_status(note_id, toggle=True)
    except Exception as e:
        return Response(str(e), status=500)
    return Response(status=200)

@core.route("/note/need/lock")
def need_auth_note():
    note_id = request.args.get("id")
    try:
        status = NoteService.need_auth_code(note_id)
    except Exception as e:
        return Response(str(e), status=500)
    return jsonify({"status": status})

@core.route('/notes', methods=['GET'])
def fetch_notes():
    try:
        tree = NoteService.fetch_catalog_tree()
    except Exception as e:
        current_app.logger.info(e)
        return Response(str(e), status=500)
    return jsonify(tree)


@core.route('/note/content', methods=['GET'])
def fetch_content():
    note_id = request.args.get('id')
    try:
        content = NoteService.fetch_note(note_id)
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)
    return content


@core.route('/note/add', methods=['POST'])
def add_note():
    title = request.form.get('title')
    pid = request.form.get('pid')
    try:
        note_id = NoteService.create_note(title=title,parent_id=pid, content="")
    except Exception as e:
        current_app.logger.error(e)
        return Response(e, status=500)
    return jsonify({"id": note_id})


@core.route('/note/update/', methods=['POST'])
def update_note():
    id = request.form.get('id')
    type = request.form.get("type")
    try:
        if type == "rename":
            title = request.form.get('title')
            NoteService.update_note_title(note_id=id, title=title)
        elif type == "position":
            parent_id = request.form.get('parent_id')
            index = request.form.get('index')
            NoteService.update_note_position(note_id=id, parent_id=parent_id,index=int(index))
        elif type == "content":
            content = request.form.get('content')
            NoteService.update_note_content(note_id=id, content=content)
        else:
            raise Exception(f"UNKNOWN PARAMETER: {type}")

    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)

    return Response(status=200)


@core.route('/note/drop', methods=['POST'])
def drop_note():
    id = request.form.get('id')
    try:
        NoteService.delete_note(id=id)
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)
    return Response(status=200)


@core.route('/note/upload/', methods=['POST'])
def upload_image():
    id = request.form.get('id')
    image = request.files.get('image')
    try:
        img_id = NoteService.create_image(note_id=id, image=image)
    except Exception as e:
        current_app.logger.error(e)
        return "error", 500

    return jsonify({'filename': f".img/{img_id}"}), 200


@core.route('/.img/<image_id>')
def download_image(image_id):
    try:
        content, mimetype = NoteService.fetch_image(image_id=image_id)
    except Exception as e:
        current_app.logger.error(f"{e}: {image_id}")
        return Response(status=500)
    return Response(content, mimetype=mimetype)


@core.route("/sync", methods=["POST"])
def sync_note():
    try:
        NoteService.netdisk_auto_sync()
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)
    return Response(status=200)


@core.route('/translator')
def text_translator():
    text = request.args.get('text')
    try:
        result = NoteService.translate_text(text)
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)
    return jsonify(result)