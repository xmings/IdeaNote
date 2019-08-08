#!/bin/python
# -*- coding: utf-8 -*-
# @File  : test_github_apiv3.py
# @Author: wangms
# @Date  : 2019/7/28
import requests
import json
from base64 import b64decode, b64encode

def test_list_folder():
    url = "https://api.github.com/repos/bmark-sync/test_github_api/contents"
    resp = requests.get(url, data={
        "ref": "master"
    })
    print(json.dumps(resp.json(), indent=4))

def test_create_folder():
    url = "https://api.github.com/repos/bmark-sync/test_github_api/contents/abc/test_create.md"
    content = b64encode("abcdef".encode("utf8")).decode("utf8")
    resp = requests.put(url, data=json.dumps({
        "message": "创建idea目录及内容文件",
        "committer": {
            "name": "bmark-sync",
            "email": "thankall@yeah.net"
        },
        "content": f"{content}",
        "branch": "master"
    }), params={
        "access_token": "c64b06c644660e1819f9077163f5f670c680dad7"
    })

    print(json.dumps(resp.json(), indent=4))

def test_delete_folder():
    test_delete_file()

def test_create_file():
    test_create_folder()

def test_delete_file():
    file_list = [
        "Docker.md",
        ".img/cd33eef0b8e011e99880a402b9518744"
    ]
    for filename in file_list:
        url = "https://api.github.com/repos/bmark-sync/notesync/contents/{}".format(filename)
        resp = requests.get(url, data={
            "ref": "master"
        })
        url = "https://api.github.com/repos/bmark-sync/notesync/contents/{}".format(filename)
        sha = resp.json()["sha"]
        resp = requests.delete(url, data=json.dumps({
            "message": "delete a file or folder",
            "sha": f"{sha}",
            "branch": "master"
        }), params={
            "access_token": "c64b06c644660e1819f9077163f5f670c680dad7"
        })
        print(resp.json())

def test_read_content():
    url = "https://api.github.com/repos/bmark-sync/note-sync-2/contents/ideanote.json"
    resp = requests.get(url, data={
        "ref": "master"
    }, params={
        "access_token": "20a50aa67bfb987a0743a0068c4e3ddb76d21780"
    })
    print(json.dumps(resp.json(), indent=4))
    return resp.json()

def test_fetch_file_sha():
    return test_read_content()["sha"]

def test_update_content():
    url = "https://api.github.com/repos/bmark-sync/test_github_api/contents/idea/init.md"
    content = b64encode("cde".encode("utf8")).decode("utf8")
    print("\ncontent: " + content)
    sha = test_fetch_file_sha()
    resp = requests.put(url, data=json.dumps({
        "message": "更新文件内容",
        "committer": {
            "name": "bmark-sync",
            "email": "thankall@yeah.net"
        },
        "sha": f"{sha}",
        "content": f"{content}",
        "branch": "master"
    }), params={
        "access_token": "be96fbcac43d1f6a6af2ec1a03e78d1557f1bd32"
    })

    print(json.dumps(resp.json(), indent=4))

def test_create_image():
    "GET /repos/:owner/:repo/git/blobs/:file_sha"
    url = "https://api.github.com/repos/xmings/JobFlow/contents/static/image/abc.png"
    resp = requests.get(url, data={
        "ref": "master"
    })
    print(json.dumps(resp.json(), indent=4))
    return resp.json()


