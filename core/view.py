#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2019/5/16
# @Brief: 简述报表功能
from . import core
from flask import render_template, request, Response, jsonify, current_app
from core.service import NoteService

@core.route("/")
def index():
    return render_template('editor.html')


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
        return Response(str(e), status=401)
    return content


@core.route('/note/add', methods=['POST'])
def add_note():
    title = request.form.get('title')
    pid = request.form.get('pid')
    try:
        note_id = NoteService.create_note(title=title,parent_id=pid, content="")
    except Exception as e:
        current_app.logger.error(e)
        return Response(e, status=401)
    return jsonify({"id": note_id})


@core.route('/note/update/', methods=['POST'])
def update_note():
    id = request.form.get('id')
    type = request.form.get("type")
    try:
        if type == "rename":
            title = request.form.get('title')
            NoteService.update_note_title(note_id=id, title=title)
        elif type in ("up-index", "down-index", "up-level"):
            prev_note_id = request.form.get('target_note_id')
            NoteService.update_note_position(note_id=id, prev_note_id=prev_note_id)
        elif type == "down-level":
            parent_id = request.form.get('target_note_id')
            NoteService.update_note_position(note_id=id, parent_id=parent_id)
        elif type == "content":
            content = request.form.get('content')
            NoteService.update_note_content(note_id=id, content=content)
        else:
            raise Exception(f"UNKNOWN PARAMETER: {type}")

    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=403)

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
        current_app.logger.error(e)
        return Response(status=403)
    return Response(content, mimetype=mimetype)


@core.route("/sync", methods=["GET"])
def sync_note():
    try:
        NoteService.sync_notes()
    except Exception as e:
        current_app.logger.info(e)
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