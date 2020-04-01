#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2019/12/20
# @Brief: 简述报表功能
import pickle
import zlib
import traceback
from base64 import b64encode
from common import conf
from threading import Thread
from .service import SyncService
from .sync_utils.netdisk_sync_utils import NetDiskSyncUtils
from .sync_utils.github_sync_utils import GithubSyncUtils
from sync import sync
from flask import request, current_app, Response, render_template

if conf.sync_method == "github":
    sync_utils = GithubSyncUtils(conf.sync_connection_info)
else:
    sync_utils = NetDiskSyncUtils(conf.sync_work_dir)

sync_service = SyncService(sync_utils)
sync_thread = Thread(target=sync_service.run)
sync_thread.daemon = True
sync_thread.start()

@sync.route('/sync/note/list')
def fetch_sync_note_list():
    try:
        result = sync_utils.fetch_sync_note_list()
    except Exception as e:
        current_app.logger.error(e)
        traceback.print_exc()
        return Response(str(e), status=500)
    return render_template('sync_note_list.html', note_list=result)


@sync.route("/sync/view/note")
def view_sync_note_content():
    try:
        note_id = request.args.get("note_id")
        version_id = request.args.get("version_id")
        note_info = sync_utils.load_note_info_by_version_note_id(version_id, note_id)
        note = pickle.loads(note_info.get("note"))
        content = zlib.decompress(note.content).decode("utf8")
        images = [zlib.decompress(pickle.loads(i).image) for i in note_info.get("images")]
        base64_images = [b64encode(i).decode() for i in images]
    except Exception as e:
        current_app.logger.error(e)
        traceback.print_exc()
        return Response(str(e), status=500)
    return render_template('sync_note_view.html', content=content, images=base64_images)


@sync.route("/sync/apply/note", methods=["POST"])
def apply_sync_note_change():
    try:
        note_id = request.form.get("note_id")
        version_id = request.form.get("version_id")
        note_info = sync_utils.load_note_info_by_version_note_id(version_id, note_id)
        sync_service.apply_change(note_info)
    except Exception as e:
        current_app.logger.error(e)
        traceback.print_exc()
        return Response(str(e), status=500)

    return Response(status=200)

@sync.route("/sync/view/latest-version")
def view_latest_version_info():
    try:
        info = sync_utils.load_version_info()
        result = ", ".join((f"{k}={v}" for k, v in info.items()))
    except Exception as e:
        current_app.logger.error(e)
        traceback.print_exc()
        return Response(str(e), status=500)

    return Response(result, status=200)


@sync.route("/sync/delete/obsolete", methods=["POST"])
def delete_obsolete_change():
    try:
        sync_utils.delete_obsolete_change()
    except Exception as e:
        current_app.logger.error(e)
        traceback.print_exc()
        return Response(str(e), status=500)

    return Response(status=200)

