#!/bin/python
# -*- coding: utf-8 -*-
# @File  : service.py
# @Author: wangms
# @Date  : 2019/12/18

import os
import pickle
import socket
import time
import zlib
import traceback
from datetime import datetime, timedelta
from core.model import Catalog, Image
from core.service import NoteService
from .model import SyncInfo, db
from common import fetch_logger, NoteStatusEnum, SyncStatusEnum
from .sync_utils.base_sync_utils import BaseSyncUtils

logger = fetch_logger(logger_name="IdeaNoteSync", log_filename="sync.log")


class SyncService(object):
    def __init__(self, sync_utils: BaseSyncUtils):
        self.sync_utils = sync_utils
        self.client_id = socket.gethostname()
        self.sync_interval = timedelta(seconds=10)

    def run(self):
        """
        > 比较latest_version_info中的client_id是否和自己相同
          > client_id不相同
            > 本地版本是否小于最新版本
              > 本地版本小于最新版本，开始以下应用日志过程
                > Note的note.sync_status是否等于SyncStatusEnum.need_sync
                  > 是，把同步过来的Note的内容append到原content末尾，并更新状态为SyncStatusEnum.need_sync，并增加本地的版本id
                  > 不是，就直接把同步过来的Note的内容写入当前的content字段，并增加本地的版本id
              > 本地版本等于最新版本
                > 本地有变更数据等待push
                  > 是，version_info文件中的change_time是否过期
                    > 是，先更新version_info文件的中client_id为本地client_id，change_time为当前系统时间，等待下一轮检查
                    > 否，等待下一轮检查
          > client_id相同
            > 本地有变更数据等待push
              > 检查version_info文件的change_time是否过期
                > 是，更新change_time为当前时间，等待下一轮检查
                > 否, push变更日志，并更新对应Note的sync_status=SyncStatusEnum.has_sync，并增加本地和version_info文件中的版本id
        TODO: 1. 接下来计划去掉总的version_id, 每个note各自维护自己的version_id，有变更就push
        :return:
        """
        while True:
            local_version_info = SyncInfo.query.first()
            try:
                not_push_change = Catalog.query.filter(Catalog.sync_status == SyncStatusEnum.need_sync.value).all()
                logger.debug(f"waiting for pushing change log: {not_push_change}")
                latest_version_info = self.sync_utils.load_version_info()
                change_time = datetime.fromisoformat(latest_version_info["change_time"])
                latest_version = int(latest_version_info["latest_version"])

                if self.client_id != latest_version_info["client_id"]:
                    if local_version_info.current_version < latest_version:
                        local_version_info.latest_version = latest_version
                        local_version_info.modification_time = datetime.now()
                        db.session.commit()
                        for ver in range(local_version_info.current_version + 1, latest_version + 1):
                            note_info = self.sync_utils.load_note_info(ver)
                            if note_info:
                                self.apply_change(note_info)
                        local_version_info.current_version = latest_version
                        local_version_info.modification_time = datetime.now()
                        db.session.commit()
                    else:
                        # 已经处于同步状态
                        if len(not_push_change) > 0 and change_time + self.sync_interval * 3 < datetime.now():
                            # 如果有未push得变更并且其他client在180秒之内没有push变更，就先修改latest_version_info，等待下一轮遍历
                            latest_version_info["client_id"] = self.client_id
                            latest_version_info["change_time"] = datetime.now().isoformat()
                            self.sync_utils.dump_version_info(latest_version_info)
                else:
                    if len(not_push_change) > 0:
                        if change_time + self.sync_interval * 1.5 < datetime.now():
                            # 如果latest_version_info中的client是自己，但chnage_time太久远，先更新change_time，等待下一轮遍历
                            latest_version_info["change_time"] = datetime.now().isoformat()
                            self.sync_utils.dump_version_info(latest_version_info)
                        else:
                            for note in not_push_change:
                                # 如果latest_version_info中的client是自己，change_time在self.sync_interval内，并且有未提交的变更，就直接push
                                latest_version += 1
                                self.push_change(note.id, latest_version)

                                latest_version_info["latest_version"] = latest_version
                                latest_version_info["change_time"] = datetime.now().isoformat()
                                self.sync_utils.dump_version_info(latest_version_info)

                                local_version_info.current_version = latest_version
                                local_version_info.latest_version = latest_version
                                local_version_info.modification_time = datetime.now()
                                db.session.commit()
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                logger.error("网盘同步线程退出")

            time.sleep(self.sync_interval.total_seconds())

    def apply_change(self, note_info):
        note = pickle.loads(note_info.get("note"))
        local_note = Catalog.query.filter(Catalog.id == note.id).first()

        if local_note and local_note.sync_status == SyncStatusEnum.need_sync.value:
            local_content = NoteService.fetch_note(note.id)
            remote_content = zlib.decompress(note.content).decode("utf8")
            content = f"{local_content}\n{'>' * 100}\n{remote_content}"
            note.content = zlib.compress(content.encode("utf8"))
            note.sync_status = SyncStatusEnum.need_sync.value
            note.status = NoteStatusEnum.need_merge.value
            note.modification_time = datetime.now()
        else:
            note.sync_status = SyncStatusEnum.has_sync.value  # 标记未同步状态

        db.session.merge(note)

        for i in note_info.get("images"):
            image = pickle.loads(i)
            db.session.merge(image)
        db.session.commit()
        logger.info(f"Succeed in applying change log: <title={note.title}, version={note_info.get('version')}>")
        return True

    def push_change(self, note_id, version):
        note_info = {}
        note = Catalog.query.filter_by(id=note_id).first()
        note_info["note"] = pickle.dumps(note)

        note_info["images"] = []
        for image in Image.query.filter_by(note_id=note_id).all():
            note_info["images"].append(pickle.dumps(image))

        note_info["id"] = note.id
        note_info["title"] = note.title
        note_info["client_id"] = self.client_id
        note_info["version"] = version
        note_info["timestamp"] = datetime.now()
        note_info["status"] = note.status
        self.sync_utils.dump_note_info(note_info)
        note.sync_status = SyncStatusEnum.has_sync.value  # 标记未同步状态
        db.session.commit()
        logger.info(f"Succeed in pushing change log: <title={note.title}, version={version}>")
        return True
