#!/bin/python
# -*- coding: utf-8 -*-
# @File  : load_note_content_to_db.py
# @Author: wangms
# @Date  : 2019/8/1
# @Brief: 简述报表功能
import os
import sqlite3
import zlib

class LoadData(object):
    def __init__(self):
        self.files_dict = {
            "E:\\MyNote": 0
        }


    def run(self):
        for parent, dirs, files in os.walk("E:\MyNote"):
            # print(parent, dirs, files)
            if parent.endswith(".img"):
                print(files)
                continue

            if "init.md" in files:
                title = os.path.basename(parent)
                path = parent
                with open(os.path.join(parent, "init.md"), "r", encoding="utf8") as f:
                    content = f.read()
                pid = self.files_dict.get(str(os.path.dirname(path)))
                note_id = self.write(title, pid, content)
                self.files_dict[path] = note_id
            else:
                continue

            for f in files:
                if f.endswith(".md") and f != "init.md":
                    title = f.replace(".md", "")
                    path = os.path.join(parent, f)
                else:
                    continue

                with open(os.path.join(parent, f), "r", encoding="utf8") as f:
                    content = f.read()

                pid = self.files_dict.get(str(os.path.dirname(path)))
                note_id = self.write(title, pid, content)
                self.files_dict[path] = note_id


    def write(self, title, pid, content):
        with sqlite3.connect("E:\\MyNote\\ideanote.db") as conn:
            cursor = conn.cursor()
            print(title, pid, content)
            cursor.execute("insert into t_catalog (title, parent_id, content) values (?, ?, ?)", (title, pid, zlib.compress(content.encode("utf8"))))
            note_id = cursor.lastrowid
            conn.commit()
        return note_id

if __name__ == '__main__':
    l = LoadData()
    l.run()
    # l.write("test", 0, "test")