#!/bin/python
# -*- coding: utf-8 -*-
# @File  : sync_by_sharding.py
# @Author: wangms
# @Date  : 2019/8/6
# @Brief: 简述报表功能
import tempfile
import os
import zlib
from hashlib import sha1
from base64 import b64encode, b64decode

import requests
import json


class Sharding(object):
    def __init__(self):
        self.block_size = 102400
        self.block_header = "wmsok".encode()
        self.datafile = "D:\\ideanote.db"
        self.work_dir = tempfile.mkdtemp()

    def slice(self):
        with open(self.datafile, "rb") as f:
            data = f.read()

        block_count = int(len(data) / self.block_size)
        for i in range(block_count):
            part = data[i * self.block_size: (i + 1) * self.block_size]
            yield f"file{i}", part

        yield f"file{block_count}", data[(block_count-1)*self.block_size:]

    def pull_block(self, name):
        url = f"https://api.github.com/repos/bmark-sync/test_github_api/contents/{name}"
        resp = requests.get(url, data={
            "ref": "master"
        })
        return b64decode(resp.json()["content"].encode())

    def push_block(self, name, content, sha=None):
        url = f"https://api.github.com/repos/bmark-sync/test_github_api/contents/file{name}"
        data = {
            "message": "创建idea目录及内容文件",
            "committer": {
                "name": "bmark-sync",
                "email": "thankall@yeah.net"
            },
            "content": f"{b64encode(content).decode('utf8')}",
            "branch": "master"
        }

        if sha:
            data["sha"] = sha
        resp = requests.put(url, data=json.dumps(data), params={
            "access_token": "4e4c78b66abba6bdfa86ccf2f46cf87aeeb40046"
        })
        assert resp.ok == True


    def calc_block_sha1(self, content):
        if isinstance(content, str):
            content = content.encode()

        s1 = sha1()
        s1.update(b"blob " + str(len(content)).encode() + b"\0" + content)
        return s1.hexdigest()


    def fetch_block_sha1(self, name):
        url = f"https://api.github.com/repos/bmark-sync/test_github_api/contents/{name}"
        resp = requests.get(url, data={
            "ref": "master"
        })
        return resp.json()["sha"]

    def push(self):
        url = "https://api.github.com/repos/bmark-sync/test_github_api/contents"
        resp = requests.get(url, data={
            "ref": "master"
        })
        remote_file_list = {}

        for i in resp.json():
            if i["name"].startswith("file"):
                remote_file_list[i["name"]] = i["sha"]

        for filename, part in self.slice():
            calc_sha1 = self.calc_block_sha1(part)
            remote_sha1 = remote_file_list.get(filename)
            if remote_sha1:
                if calc_sha1 != remote_sha1:
                    print(f"update: {filename}")
                    self.push_block(filename, part, remote_sha1)
                else:
                    print(f"not change: {filename}")
            else:
                print(f"add: {filename}")
                self.push_block(filename, part)

    def pull(self):
        url = "https://api.github.com/repos/bmark-sync/test_github_api/contents"
        resp = requests.get(url, data={
            "ref": "master"
        })

        with open("d:\\ideanote.db", "ab") as f:
            for i in resp.json():
                if i["name"].startswith("file"):
                    f.write(self.pull_block(i["name"]))


if __name__ == '__main__':
    s = Sharding()
    #s.push()
    s.pull()