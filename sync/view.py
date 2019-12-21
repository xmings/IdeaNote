#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2019/12/20
# @Brief: 简述报表功能
from common import conf
from threading import Thread
from .service import SyncService
from .sync_utils.netdisk_sync_utils import NetDiskSyncUtils
from .sync_utils.github_sync_utils import GithubSyncUtils
from sync import sync
from flask import request, current_app, Response, jsonify

#sync_utils = NetDiskSyncUtils(conf.sync_work_dir)
sync_utils = GithubSyncUtils(conf.sync_connection_info)
sync_service = SyncService(sync_utils)

sync_thread = Thread(target=sync_service.run)
sync_thread.daemon = True
sync_thread.start()

@sync.route('/sync/note_list')
def fetch_sync_note_list():
    try:
        note_list = sync_utils.fetch_sync_note_list()
    except Exception as e:
        current_app.logger.error(e)
        return Response(str(e), status=500)
    return jsonify(note_list)


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