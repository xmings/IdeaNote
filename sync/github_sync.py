#!/bin/python
# -*- coding: utf-8 -*-
# @File  : github_sync.py
# @Author: wangms
# @Date  : 2019/7/29
# @Brief: 简述报表功能
from sync.base_sync import BaseSync
from common import utils, Result
import requests
import json
from datetime import datetime
from base64 import b64encode, b64decode

class GithubSync(BaseSync):
    def __init__(self, local_metadata):
        super(GithubSync, self).__init__()
        conn = utils.conf.remote_connection_info()
        self.owner = conn.get("owner")
        self.email = conn.get("email")
        self.repo = conn.get("repo")
        self.access_token = conn.get("access_token")
        self.branch = conn.get("branch")
        self.metadata_file = utils.conf.metadata_file
        self.local_metadata = local_metadata
        self.fetch_remote_metadata()
        self.version_interval = self.metadata_version_interval(self.local_metadata)
        assert self.version_interval > 0, f"VERSION INTERVAL EXCEPTIION: {self.version_interval}"

        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.sync_batch = str(datetime.now())

    def fetch_remote_metadata(self):
        url = f"{self.base_url}/contents/{self.metadata_file}"
        resp = requests.get(url, data={
            "ref": self.branch
        })

        self.remote_metadata = b64decode(resp.json()["content"].encode("utf8")).decode("utf8")
        return self.remote_metadata

    def metadata_version_interval(self, local_metadata):
        local_version = self.local_metadata["sha"]
        remote_version = self.remote_metadata["sha"]
        url = f"{self.base_url}/commits"

        resp = requests.get(url)
        sha_list = [i["sha"] for i in resp]
        local_version_index = sha_list.index(local_version)
        remote_version_index = sha_list.index(remote_version)

        return local_version_index - remote_version_index

    def create_diff_record(self):
        last_sync_time = self.local_metadata["last_sync_time"]

        new_notes = {}
        change_notes = {}
        delete_notes = {}

        for id, v in self.local_metadata.get("items").items():
            if v["create_time"] >= last_sync_time:
                new_notes[id] = self._auto_complete_path(id)
            elif v["modification_time"] >= last_sync_time:
                change_notes[id] = self._auto_complete_path(id)

        if self.version_interval == 0:
            # 落后1个以上的版本，不会再处理删除
            for id, v in self.remote_metadata.get("items").items():
                if id not in self.local_metadata:
                    delete_notes[id] = self._auto_complete_path(id, "remote")

        return Result(True, {
            "version_interval": self.version_interval,
            "new": new_notes,
            "change": change_notes,
            "delete": delete_notes
        })

    def fetch_remote_path_content(self, path):
        url = f"{self.base_url}/contents/{path}"
        resp = requests.get(url, data={
            "ref": self.branch
        })
        # directory
        result = resp.json()
        if (isinstance(resp.json(), list)):
            content = {
                "type": "dir",
                "children": [
                    {
                        "type": i["type"],
                        "path": i["path"],
                        "sha": i["sha"]
                     } for i in result
                ]
            }
        else:
            content = {
                "type": "file",
                "path": result["path"],
                "sha": result["sha"],
                "content": b64decode(result["content"].encode("utf8")).decode("utf8")
            }

        return content

    def update_remote_note_content(self, path, sha, content):
        url = f"{self.base_url}/contents/{path}"
        content = b64encode("cde".encode("utf8")).decode("utf8")
        resp = requests.put(url, data=json.dumps({
            "message": self.sync_batch,
            "committer": {
                "name": self.owner,
                "email": self.email
            },
            "sha": sha,
            "content": content,
            "branch": self.branch
        }), params={
            "access_token": self.access_token
        })

        return resp.ok


    def delete_remote_note(self, path, sha):
        url = f"{self.base_url}/contents/{path}"
        resp = requests.delete(url, data=json.dumps({
            "message": self.sync_batch,
            "sha": sha,
            "branch": self.branch
        }), params={
            "access_token": self.access_token
        })
        return resp.ok


    def _auto_complete_path(self, id: int, where="local"):
        path = ''
        metadata = self.local_metadata if where == "local" else self.remote_metadata
        item = metadata.get(int(id))
        while item["id"] > 0:
            path = f"{item['title']}/{path}" if path else item["title"]
            item = metadata.get(item["parent_id"])

        if where == "local":
            path = path.replace("/", "\\")

        return path







