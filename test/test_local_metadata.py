#!/bin/python
# -*- coding: utf-8 -*-
# @File  : test_local_metadata.py
# @Author: wangms
# @Date  : 2019/8/1

from dataclasses import dataclass
import sqlite3


@dataclass
class MetaData(object):
    id: int
    title: str
    parent_id: int
    seq_no: int
    status: int
    creation_time: str
    modification_time: str


def main():
    local_metadata = {}
    with sqlite3.connect("E:\\MyNote\\ideanote.db") as conn:
        cursor = conn.cursor()
        cursor.execute("select id,title,parent_id,seq_no,status,creation_time,modification_time from t_catalog")
        for id,title,parent_id,seq_no,status,creation_time,modification_time in cursor:
            local_metadata[id] = {
                "title": title,
                "parent_id": parent_id,
                "seq_no": seq_no,
                "status": status,
                "creation_time": str(creation_time),
                "modification_time": str(modification_time)
            }



