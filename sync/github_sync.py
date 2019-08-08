#!/bin/python
# -*- coding: utf-8 -*-
# @File  : github_center.py
# @Author: wangms
# @Date  : 2019/7/29
# @Brief: 简述报表功能
from sync.base_sync import BaseSync
from common import utils
import requests
import json
from datetime import datetime
from base64 import b64encode, b64decode


class GithubSync(BaseSync):
    def __init__(self):
        conn = utils.conf.remote_connection_info
        self.owner = conn.get("owner")
        self.email = conn.get("email")
        self.repo = conn.get("repo")
        self.access_token = conn.get("access_token")
        self.branch = conn.get("branch")
        self.commit_comment = str(datetime.now())
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        super(GithubSync, self).__init__()

    def fetch_metadata_and_sha(self):
        url = f"{self.base_url}/contents/{self.metadata_file}"
        resp = requests.get(url, data={
            "ref": self.branch
        })
        result = resp.json()
        if not resp.ok:
            return {}, None
        return json.loads(b64decode(result["content"].encode("utf8")).decode("utf8")), result["sha"]

    def update_metadata(self):
        url = f"{self.base_url}/contents/{self.metadata_file}"
        data = {
            "message": self.commit_comment,
            "committer": {
                "name": self.owner,
                "email": self.email
            },
            "content": b64encode(json.dumps(self.remote_metadata,
                                            ensure_ascii=False,
                                            indent=4).encode()).decode("utf8"),
            "branch": self.branch
        }
        if self.remote_metadata_sha:
            data["sha"] = self.remote_metadata_sha
        resp = requests.put(url, data=json.dumps(data), params={
            "access_token": self.access_token
        })
        self.remote_metadata_sha = resp.json()["content"]["sha"]
        return resp.ok

    def fetch_remote_note(self, note_id):
        url = f"{self.base_url}/contents/{self.remote_metadata[note_id]['relative_path']}"
        resp = requests.get(url, data={
            "ref": self.branch
        })
        return b64decode(resp.json()["content"].encode("utf8")).decode("utf8")

    def create_remote_note(self, note_id, content):
        relative_path = self._auto_gen_note_path(note_id=note_id)
        url = f"{self.base_url}/contents/{relative_path}"
        resp = requests.put(url, data=json.dumps({
            "message": self.commit_comment,
            "committer": {
                "name": self.owner,
                "email": self.email
            },
            "content": b64encode(content).decode("utf8"),
            "branch": self.branch
        }), params={
            "access_token": self.access_token
        })
        self.remote_metadata[note_id]["sha"] = resp.json()["content"]["sha"]
        self.remote_metadata[note_id]["relative_path"] = relative_path
        return resp.ok

    def update_remote_note(self, note_id, content):
        url = f"{self.base_url}/contents/{self.remote_metadata[note_id]['relative_path']}"
        resp = requests.put(url, data=json.dumps({
            "message": self.commit_comment,
            "committer": {
                "name": self.owner,
                "email": self.email
            },
            "sha": self.remote_metadata[note_id]["sha"],
            "content": b64encode(content).decode("utf8"),
            "branch": self.branch
        }), params={
            "access_token": self.access_token
        })
        self.remote_metadata[note_id]["sha"] = resp.json()["content"]["sha"]
        return resp.ok

    def delete_remote_note(self, note_id):
        url = f"{self.base_url}/contents/{self.remote_metadata[note_id]['relative_path']}"
        resp = requests.delete(url, data=json.dumps({
            "message": self.commit_comment,
            "sha": self.remote_metadata[note_id]["sha"],
            "branch": self.branch
        }), params={
            "access_token": self.access_token
        })
        return resp.ok

    def fetch_remote_image(self, note_id, image_id):
        url = f"{self.base_url}/contents/{self.remote_metadata[note_id][image_id]['img_rel_path']}"
        resp = requests.get(url, data={
            "ref": self.branch
        })
        return b64decode(resp.json()["content"].encode("utf8"))

    def create_remote_image(self, note_id, image_id, content):
        img_rel_path = self._auto_gen_image_path(note_id, image_id)
        url = f"{self.base_url}/contents/{img_rel_path}"
        resp = requests.put(url, data=json.dumps({
            "message": self.commit_comment,
            "committer": {
                "name": self.owner,
                "email": self.email
            },
            "content": b64encode(content).decode("utf8"),
            "branch": self.branch
        }), params={
            "access_token": self.access_token
        })
        self.remote_metadata[note_id]["images"][image_id]["sha"] = resp.json()["content"]["sha"]
        self.remote_metadata[note_id]["images"][image_id]["img_rel_path"] = img_rel_path
        return resp.ok

    def update_remote_image(self, note_id, image_id, content):
        url = f"{self.base_url}/contents/{self.remote_metadata[note_id][image_id]['img_rel_path']}"
        resp = requests.put(url, data=json.dumps({
            "message": self.commit_comment,
            "committer": {
                "name": self.owner,
                "email": self.email
            },
            "sha": self.remote_metadata[note_id]["sha"],
            "content": b64encode(content).decode("utf8"),
            "branch": self.branch
        }), params={
            "access_token": self.access_token
        })
        self.remote_metadata[note_id]["sha"] = resp.json()["content"]["sha"]
        return resp.ok

    def delete_remote_image(self, note_id, image_id):
        url = f"{self.base_url}/contents/{self.remote_metadata[note_id][image_id]['img_rel_path']}"
        resp = requests.delete(url, data=json.dumps({
            "message": self.commit_comment,
            "sha": self.remote_metadata[note_id]["images"][image_id]["sha"],
            "branch": self.branch
        }), params={
            "access_token": self.access_token
        })
        return resp.ok


if __name__ == '__main__':
    sync = GithubSync()
    sync.run()
    print(datetime.now())
