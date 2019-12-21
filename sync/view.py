#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2019/12/20
# @Brief: 简述报表功能
import pickle
import zlib
import traceback
from base64 import b64encode, b64decode
from common import conf
from threading import Thread
from .service import SyncService
from .sync_utils.netdisk_sync_utils import NetDiskSyncUtils
from .sync_utils.github_sync_utils import GithubSyncUtils
from sync import sync
from flask import request, current_app, Response, jsonify, render_template

if conf.sync_method == "github":
    sync_utils = GithubSyncUtils(conf.sync_connection_info)
else:
    sync_utils = NetDiskSyncUtils(conf.sync_work_dir)

sync_service = SyncService(sync_utils)
sync_thread = Thread(target=sync_service.run)
sync_thread.daemon = True
sync_thread.start()

@sync.route('/sync/note_list')
def fetch_sync_note_list():
    try:
        result = sync_utils.fetch_sync_note_list()
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)
    return render_template('sync_note_list.html', note_list=result)


@sync.route('/sync/note_info')
def parse_note_info_header():
    note_id = request.args.get('note_id')
    version_id = request.args.get('version_id')
    try:
        if version_id:
            result = sync_utils.load_note_info(int(version_id))
        elif note_id:
            result = sync_utils.load_latest_note_info(note_id)
        else:
            result = {}

        if result:
            result.pop("content")
            result.pop("images")
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)
    return jsonify(result)

@sync.route("/sync/view/note")
def sync_note_view():
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