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
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"

    def remote_fetch_metadata(self):
        url = f"{self.base_url}/contents/{self.metadata_file}"
        resp = requests.get(url, data={
            "ref": self.branch
        })

        self.remote_metadata = b64decode(resp.json()["content"].encode("utf8")).decode("utf8")
        return json.loads(self.remote_metadata)

    def remote_fetch(self, relative_path, type):
        if type == "metadata":
            relative_path = relative_path
        elif type == "node":
            relative_path += ".md"
        elif type == "image":
            relative_path += type

        url = f"{self.base_url}/contents/{relative_path}"
        resp = requests.get(url, data={
            "ref": self.branch
        })
        result = b64decode(resp.json()["content"].encode("utf8"))
        return result.decode("utf8") if type != "image" else result

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








