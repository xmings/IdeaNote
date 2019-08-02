#!/bin/python
# -*- coding: utf-8 -*-
# @File  : github_center.py
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
    def __init__(self):
        super(GithubSync, self).__init__()
        conn = utils.conf.remote_connection_info()
        self.owner = conn.get("owner")
        self.email = conn.get("email")
        self.repo = conn.get("repo")
        self.access_token = conn.get("access_token")
        self.branch = conn.get("branch")
        self.metadata_file = utils.conf.metadata_file
        self.fetch_remote_metadata()

        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.sync_batch = str(datetime.now())

    def fetch_remote_metadata(self):
        url = f"{self.base_url}/contents/{self.metadata_file}"
        resp = requests.get(url, data={
            "ref": self.branch
        })

        self.remote_metadata = b64decode(resp.json()["content"].encode("utf8")).decode("utf8")
        return self.remote_metadata

    def _metadata_version_interval(self):
        remote_sha = self.remote_metadata["sha"]
        url = f"{self.base_url}/commits"

        resp = requests.get(url)
        sha_list = [i["sha"] for i in resp]
        local_version_index = sha_list.index(self.local_sha)
        remote_version_index = sha_list.index(remote_sha)

        return local_version_index - remote_version_index

    def create_diff_record(self):
        interval = self._metadata_version_interval()
        assert interval <= 0, f"UNKNOWN VERSION INTERVAL: {interval}"
        new_notes = {}
        change_notes = {}
        delete_notes = {}

        if interval == 0:
            for k, v in self.local_change:
                if k == "update":
                    sha = self.update_remote_note_content(v["path"], v["sha"], v["content"])
                    self.local_change[k]["new_sha"] = sha
                elif k == "delete":
                    self.delete_remote_note(v["path"], v["sha"])
                self.local_change[k]["status"] = 1

            # 更新远程metadata文件

        else:
            # 应用最近sync以来的远程服务器变更到本地，如果某note本地副本内容也发生改变，则提示
            # 上传本地其他变更或删除note到服务器，并先由用户确认

            pass


        # 上传图片



        return Result(True, {
            "version_interval": interval,
            "new": new_notes,
            "change": change_notes,
            "delete": delete_notes
        })


    def run(self):
        pass


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








