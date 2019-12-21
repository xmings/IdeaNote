#!/bin/python
# -*- coding: utf-8 -*-
# @File  : github_sync_utils.py
# @Author: wangms
# @Date  : 2019/12/20
# @Brief: 简述报表功能
import requests
import json
import pickle
from base64 import b64encode, b64decode
from common import conf
from .base_sync_utils import BaseSyncUtils


class GithubSyncUtils(BaseSyncUtils):
    def __init__(self):
        conn = conf.remote_connection_info
        self.owner = conn.get("owner")
        self.email = conn.get("email")
        self.repo = conn.get("repo")
        self.access_token = conn.get("access_token")
        self.branch = conn.get("branch")
        self.version_info_filename = "version_info.txt"
        self.note_info_file_suffix = ".txt"
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"

    def _fetch_content_response(self, filename=None):
        url = f"{self.base_url}/contents/{filename}"
        resp = requests.get(url, data={
            "ref": self.branch
        }, params={
            "access_token": self.access_token
        })
        return resp.json()

    def _push_file_with_reponse(self, filename, message, content, sha=None):
        url = f"{self.base_url}/contents/{filename}"
        data = {
            "message": message,
            "committer": {
                "name": self.owner,
                "email": self.email
            },
            "content": content,
            "branch": self.branch
        }

        if sha:
            data["sha"] = sha
        resp = requests.put(url, data=json.dumps(data), params={
            "access_token": self.access_token
        })
        return resp.json()

    def load_version_info(self) -> dict:
        resp = self._fetch_content_response(self.version_info_filename)
        self.version_info_sha = resp.get("sha")
        return b64decode(resp.get("content").encode("utf8")).decode("utf8")

    def dump_version_info(self, version_info: dict) -> bool:
        resp = self._push_file_with_reponse(
            filename=self.version_info_filename,
            message=f"{version_info.get('client_id')}##{version_info.get('change_time')}##{version_info.get('latest_version')}",
            content=b64encode(json.dumps(version_info,ensure_ascii=False,indent=4).encode("utf8")).decode("utf8"),
            sha=self.version_info_sha)
        self.version_info_sha = resp.get("content").get("sha")
        return resp.ok

    def load_note_info(self, version: int) -> dict:
        filename = None
        for i in self._fetch_content_response():
            base_filename = i.get("name")[:-len(self.note_info_file_suffix)]
            version_id, note_id = base_filename.split("-")
            if version_id == version:
                filename = i.get("name")
                break
        resp = self._fetch_content_response(filename=filename)
        return b64decode(resp.get("content").encode("utf8")).decode("utf8")

    def load_latest_note_info(self, note_id) -> dict:
        filename = None
        for i in self._fetch_content_response():
            base_filename = i.get("name")[:-len(self.note_info_file_suffix)]
            version_id, note_id_ = base_filename.split("-")
            if note_id_ == note_id:
                filename = i.get("name")
                break
        resp = self._fetch_content_response(filename=filename)
        return b64decode(resp.get("content").encode("utf8")).decode("utf8")

    def dump_note_info(self, note_info: dict) -> bool:
        resp = self._push_file_with_reponse(
            filename=f"{note_info.get('version')}-{note_info.get('id')}{self.note_info_file_suffix}",
            message=f"{note_info.get('title')}##{note_info.get('timestamp')}",
            content=pickle.dumps(note_info)
        )
        return resp.ok
