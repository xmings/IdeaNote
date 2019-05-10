#!/bin/python
# -*- coding: utf-8 -*-
# @File  : test_catalogdb.py
# @Author: wangms
# @Date  : 2019/5/10
# @Brief: 简述报表功能

from catalogdb import CatalogDB
from catalogdb.model import Item,User
from datetime import datetime

class app():
    pass

app.config = {}
app.config["JSON_DB_FILE"] = "d:\\"
app.config["CREATE_DB_IF_NOT_FOUND"] = True
catalog = CatalogDB(app)

class TestCatalogDB():

    def test_insert_item(self):
        catalog.insert_item(Item(
            id=2,
            title="test2",
            type="file",
            parent_id=0,
            children=[],
            icon_path="",
            file_hash="",
            file_path="",
            status=1,
            creation_time=datetime.now(),
            modification_time=datetime.now()
        ))

    def test_update_item(self):
        catalog.update_item(Item(
            id=2,
            title="test",
            type="directory",
            parent_id=0,
            children=[],
            icon_path="",
            file_hash="",
            file_path="",
            status=1,
            creation_time=datetime.now(),
            modification_time=datetime.now()
        ))

    def test_delete_item(self):
        catalog.delete_item(Item(
            id=3,
            title="test",
            type="directory",
            parent_id=0,
            children=[],
            icon_path="",
            file_hash="",
            file_path="",
            status=1,
            creation_time=datetime.now(),
            modification_time=datetime.now()
        ))

    def test_select_item_by_id(self):
        print(catalog.select_item_by_id(1))

    def test_insert_user(self):
        catalog.insert_user(User(
            username='w',
            password='w',
            login_host='my',
            login_time=datetime.now(),
            edit_start_time=datetime.now(),
            edit_item_id=1
        ))

    def test_update_user(self):
        catalog.update_user(User(
            username='w',
            password='w123',
            login_host='my',
            login_time=datetime.now(),
            edit_start_time=datetime.now(),
            edit_item_id=2
        ))
