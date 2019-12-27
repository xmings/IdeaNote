#!/bin/python
# -*- coding: utf-8 -*-
# @File  : github_sync_utils.py
# @Author: wangms
# @Date  : 2019/12/20
# @Brief: 简述报表功能
import os
import requests
import json
import pickle
import socket
from datetime import datetime, timedelta
from base64 import b64encode, b64decode
from .base_sync_utils import BaseSyncUtils
from common import Resp


class GithubSyncUtils(BaseSyncUtils):
    def __init__(self, github_config):
        self.owner = github_config.get("owner")
        self.email = github_config.get("email")
        self.repo = github_config.get("repo")
        self.access_token = github_config.get("access_token")
        self.branch = github_config.get("branch")
        self.version_info_filename = "version_info.txt"
        self.version_info_sha = None
        self.note_info_file_suffix = ".txt"
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"

        resp = self._fetch_content_response(self.version_info_filename)
        if resp.status:
            self.version_info_sha = resp.content.get("sha")
        else:
            raise Exception(f"Not found {self.version_info_filename}")

    def init_version_info(self):
        version_info = {
            "latest_version": 0,
            "client_id": socket.gethostname(),
            "change_time": datetime.now().isoformat()
        }
        self.dump_version_info(version_info)

    def _fetch_content_response(self, filename=None) -> Resp:
        url = f"{self.base_url}/contents/{filename}"
        resp = requests.get(url, data={
            "ref": self.branch
        }, params={
            "access_token": self.access_token
        })
        return Resp(status=resp.ok, content=resp.json())

    def _push_file_with_reponse(self, filename, message, content, sha=None) -> Resp:
        url = f"{self.base_url}/contents/{filename}"
        data = {
            "message": message,
            "committer": {
                "name": self.owner,
                "email": self.email
            },
            "content": b64encode(content).decode("utf8"),
            "branch": self.branch
        }

        if sha:
            data["sha"] = sha
        resp = requests.put(url, data=json.dumps(data), params={
            "access_token": self.access_token
        })
        return Resp(resp.ok, resp.json())

    def _delete_file_with_reponse(self, filename, message, sha) -> Resp:
        url = f"{self.base_url}/contents/{filename}"
        data = {
            "message": message,
            "sha": sha,
            "branch": self.branch
        }
        resp = requests.delete(url, data=json.dumps(data), params={
            "access_token": self.access_token
        })

        return Resp(resp.ok, resp.json())

    def load_version_info(self) -> dict:
        resp = self._fetch_content_response(self.version_info_filename)
        self.version_info_sha = resp.content.get("sha")
        return json.loads(b64decode(resp.content.get("content").encode("utf8")).decode("utf8"))

    def dump_version_info(self, version_info: dict) -> bool:
        resp = self._push_file_with_reponse(
            filename=self.version_info_filename,
            message=f"{version_info.get('client_id')}##{version_info.get('change_time')}##{version_info.get('latest_version')}",
            content=json.dumps(version_info, ensure_ascii=False, indent=4).encode("utf8"),
            sha=self.version_info_sha if self.version_info_sha else None)
        self.version_info_sha = resp.content.get("sha")
        return resp.status

    def load_note_info(self, version: int) -> dict:
        filename = None
        for i in self._fetch_content_response().content:
            base_filename = i.get("name")[:-len(self.note_info_file_suffix)]
            version_id, note_id = base_filename.split("-")
            if version_id == version:
                filename = i.get("name")
                break
        resp = self._fetch_content_response(filename=filename)
        return pickle.loads(b64decode(resp.content.get("content").encode("utf8")))

    def load_latest_note_info(self, note_id) -> dict:
        filename = None
        for i in self._fetch_content_response().content:
            base_filename = i.get("name")[:-len(self.note_info_file_suffix)]
            version_id, note_id_ = base_filename.split("-")
            if note_id_ == note_id:
                filename = i.get("name")
                break
        resp = self._fetch_content_response(filename=filename)
        return pickle.loads(b64decode(resp.content.get("content").encode("utf8")))

    def load_note_info_by_version_note_id(self, version, note_id) -> dict:
        filename = f"{version}-{note_id}{self.note_info_file_suffix}"
        resp = self._fetch_content_response(filename=filename)
        return pickle.loads(b64decode(resp.content.get("content").encode("utf8")))

    def dump_note_info(self, note_info: dict) -> bool:
        resp = self._push_file_with_reponse(
            filename=f"{note_info.get('version')}-{note_info.get('id')}{self.note_info_file_suffix}",
            message=f"{note_info.get('title')}##{note_info.get('timestamp')}",
            content=pickle.dumps(note_info)
        )
        return resp.status

    def fetch_sync_note_list(self):
        note_list = self._fetch_content_response()
        result = []
        for i in note_list.content:
            filename = i.get("name")
            version_id, note_id = filename[:-len(self.note_info_file_suffix)].split("-")
            if not version_id or not note_id: continue
            note = self.load_note_info_by_version_note_id(version_id, note_id)
            result.append({
                "version_id": note.get("version"),
                "note_id": note.get("id"),
                "filename": filename,
                "title": note.get("title"),
                "from_client": note.get("client_id"),
                "timestamp": note.get("timestamp"),
                "_sha": i.get("sha")
            })
        return result

    def delete_obsolete_change(self, day: int = 30):
        for note in self.fetch_sync_note_list():
            if note.get("timestamp") + timedelta(days=day) < datetime.now():
                self._delete_file_with_reponse(note.get("filename"), f"obsolete, timestamp: {datetime.now().isoformat()}", note.get("_sha"))
        return True
