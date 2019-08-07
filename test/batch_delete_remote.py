#!/bin/python
# -*- coding: utf-8 -*-
# @File  : batch_delete_remote.py
# @Author: wangms
# @Date  : 2019/8/8
import requests
import json

def test_batch_delete_remote():
    url = "https://api.github.com/repos/bmark-sync/notesync/contents"
    resp = requests.get(url, data={
        "ref": "master"
    })
    for v in resp.json():
        print(v)
        if v["type"] == "file" and v["name"] != "README.md":
            url = "https://api.github.com/repos/bmark-sync/notesync/contens/{}".format(v["name"])
            resp = requests.delete(url, data=json.dumps({
                "message": "delete a file or folder",
                "sha": v["sha"],
                "branch": "master"
            }), params={
                "access_token": "c64b06c644660e1819f9077163f5f670c680dad7"
            })

            print(resp.json())


