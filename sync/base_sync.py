#!/bin/python
# -*- coding: utf-8 -*-
# @File  : base_center.py
# @Author: wangms
# @Date  : 2019/7/27
from core.model import Catalog, SyncRecord, Image
from sqlalchemy import or_
import zlib
import json
from hashlib import sha1
from common import utils
from datetime import datetime


class BaseSync(object):
    def __init__(self):
        last_sync = SyncRecord.query.order_by(SyncRecord.creation_time.desc()).first()
        self.local_sha = last_sync.sha
        self.last_sync_time = last_sync.creation_time
        self.remote_metadata = []
        self.metadata_file = utils.conf.metadata_file

    @NotImplemented
    def remote_fetch_metadata(self):
        pass

    @NotImplemented
    def remote_fetch(self, relative_path):
        pass

    @NotImplemented
    def remote_create(self, relative_path, content):
        pass

    @NotImplemented
    def remote_update(self, relative_path, sha, content):
        pass

    @NotImplemented
    def remote_delete(self, relative_path, sha):
        pass

    def _auto_complete_path(self, note_id: int):
        path = ''
        note = Catalog.query.filter(Catalog.id == note_id).first()
        while note.id > 1:
            path = f"{note.title}/{path}" if path else note.title
            note = Catalog.query.filter(Catalog.id == note.parent_id).first()

        return path

    def _is_equal(self, local_content, remote_note_sha):
        s1 = sha1()
        s1.update(f"blob {len(local_content)}\0{local_content}".encode("utf8"))
        return s1.hexdigest() == remote_note_sha

    def run(self):
        # 事务性，所有同步再成功之后统一清楚标记
        self.remote_metadata = self.remote_fetch_metadata()
        if self.remote_metadata["sha"] != self.local_sha:
            # 同步远程到本地
            for id, v in self.remote_metadata.items():
                local_note = Catalog.query.filter(Catalog.id == id).first()
                # remote changed file after last sync
                if v["modification_time"] > self.last_sync_time:
                    # last_sync_time之前创建，之后修改
                    if local_note:
                        if local_note.modification_time > self.last_sync_time:
                            # 本地也发生改变
                            if not self._is_equal(zlib.decompress(local_note.content).decode("utf8"), v["sha"]):
                                # 内容冲突
                                local_note.remote_content = zlib.compress(
                                    self.remote_fetch(v["relative_path"]).encode("utf8"))
                        else:
                            # 本地未改变，直接覆盖
                            local_note.content = zlib.compress(self.remote_fetch(v["relative_path"]).encode("utf8"))
                    else:
                        # 本地丢失，直接插入
                        local_note = Catalog(id=v["id"], content=zlib.compress(
                            self.remote_fetch(v["relative_path"]).encode("utf8")))
                else:
                    # v["creation_time"] > self.last_sync_time
                    local_note = Catalog(id=v["id"],
                                         content=zlib.compress(self.remote_fetch(v["relative_path"]).encode("utf8")))

                local_note.status = 3  # pull
                local_note.title = v["title"]
                local_note.sha = v["sha"]
                local_note.seq_no = v["seq_no"]
                local_note.parent_id = v["parent_id"]
                local_note.creation_time = v["creation_time"]
                local_note.creation_time = v["modification_time"]

            # 远程已删除本地未删除
            for n in Catalog.query.filter(Catalog.creation_time < self.last_sync_time, Catalog.status == 1).all():
                if not self.remote_metadata.get(n.id):
                    n.status = 11 if n.modification_time > self.last_sync_time else -1
                    n.modification_time = datetime.now()

        # 同步本地到远程
        for n in Catalog.query.all():
            if n.status == 1:
                if n.creation_time > self.last_sync_time:
                    # 上传新建note(新建的note可能基于一个已经删除的父目录)
                    n.sha = self.remote_create(self._auto_complete_path(n.id), zlib.compress(n.content.encode("utf8")))
                elif n.modification_time > self.last_sync_time:
                    # 上传更新的note
                    remote_note = self.remote_metadata[n.id]
                    local_note_content = zlib.decompress(n.content).decode("utf8")
                    relative_path = self._auto_complete_path(n.id)
                    if n.title != remote_note:
                        self.remote_delete(remote_note["relative_path"], remote_note["sha"])
                        self.remote_create(relative_path, zlib.compress(n.content.encode("utf8")))
                    elif not self._is_equal(local_note_content, remote_note["sha"]):
                        self.remote_update(remote_note["relative_path"],remote_note["sha"],local_note_content)
            elif n.status == -1:
                # 上传删除的note(删除的note可能包含一个刚同步下的子孙节点)
                if n.creation_time < self.last_sync_time:
                    remote_note = self.remote_metadata.get(n.id)
                    if remote_note:
                        self.remote_delete(remote_note["relative_path"], remote_note["sha"])



