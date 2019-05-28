#!/bin/python
# -*- coding: utf-8 -*-
# @File  : test_catalogdb.py
# @Author: wangms
# @Date  : 2019/5/10
# @Brief: 简述报表功能

from catalogdb import DBOperator
from catalogdb.model import Item,User
from datetime import datetime

class app():
    pass

app.config = {}
app.config["JSON_DB_FILE"] = "d:\\"
app.config["CREATE_DB_IF_NOT_FOUND"] = True
catalog = DBOperator(app)

class TestCatalogDB():

    def test_insert_item(self):
        catalog.insert_item(Item(
            title="test10",
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
        item = catalog.select_item_by_id(1)
        item.title="test3"
        catalog.update_item(item)

    def test_delete_item(self):
        item = catalog.select_item_by_id(1)
        catalog.delete_item(item)

    def test_select_item_by_id(self):
        print(catalog.select_item_by_id(2))

    def test_insert_user(self):
        user = User(
            username='w',
            password='w',
            regist_time= datetime.now()
        )
        catalog.insert_user(user)

    def test_update_user(self):
        user = catalog.select_user_by_username("w")
        user.edit_item_id = 2
        catalog.update_user(user)

