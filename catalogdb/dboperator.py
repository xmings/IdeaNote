#!/bin/python
# -*- coding: utf-8 -*-
# @File  : dboperator.py
# @Author: wangms
# @Date  : 2019/5/9
# @Brief: 简述报表功能
import os, json, tempfile, re
from threading import Lock
from datetime import datetime
from catalogdb.model import Item, User

BASE_JSON_DB = {
    "title": "MyBase",
    "items": {},
    "lock_item_ids": [],
    "last_sync_sha": "",
    "last_sync_time": "",
    "users": {},
    "version": 0,
    "modification_time": ""
}

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
ITEM_ROOT_ID = 0
lock = Lock()

try:
    import cPickle as pickle
except ImportError:
    import pickle


class JsonEncoderForPersistence(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Item):
            return {
                "id": obj.id,
                "title": obj.title,
                "type": obj.type,
                "parent_id": obj.parent_id,
                "icon_path": obj.icon_path,
                "file_path": obj.file_path,
                "file_hash": obj.file_hash,
                "status": obj.status,
                "creation_time": obj.creation_time.strftime(DATETIME_FORMAT) if obj.creation_time else None,
                "modification_time": obj.modification_time.strftime(DATETIME_FORMAT) if obj.modification_time else None
            }
        elif isinstance(obj, User):
            return {
                "username": obj.username,
                "password": obj.password,
                "regist_time": obj.regist_time.strftime(DATETIME_FORMAT) if obj.regist_time else None,
                "login_time": obj.login_time.strftime(DATETIME_FORMAT) if obj.login_time else None,
                "login_host": obj.login_host,
                "edit_item_id": obj.edit_item_id,
                "edit_start_time": obj.edit_start_time.strftime(DATETIME_FORMAT) if obj.edit_start_time else None
            }
        elif isinstance(obj, datetime):
            return obj.strftime(DATETIME_FORMAT)
        return json.JSONEncoder.default(self, obj)


class JsonEncoderForFrontEnd(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Item):
            if o.children:
                return {
                    "id": o.id,
                    "name": o.title,
                    "open": False,
                    "children": o.children
                }
            return {
                "id": o.id,
                "name": o.title,
                "open": False
            }
        return super().default(o)


class DBOperator(object):
    def __init__(self, app=None):
        self.default_db_file_name = "json.db"
        self._temp_db_file = os.path.join(tempfile.gettempdir(), self.default_db_file_name)
        self.db_file = None
        self._catalog_dict = {}
        self._item_dict = {}
        self._user_dict = {}
        self._current_item_id = ITEM_ROOT_ID
        if app:
            self.init_db(app)

    def init_db(self, app):
        self.db_file = app.config.get("JSON_DB_FILE")
        create = app.config.get("CREATE_DB_IF_NOT_FOUND")
        if os.path.isdir(self.db_file):
            child_file = os.path.join(self.db_file, self.default_db_file_name)
            if os.path.isfile(child_file):
                self.db_file = child_file
            elif create:
                open(child_file, "w", encoding="utf8").close()
                self.db_file = child_file
            else:
                raise Exception("JSON DB FILE NOT FOUND")

        try:
            with open(self.db_file, 'r', encoding="utf8") as f:
                self._catalog_dict = json.loads(f.read())
        except:
            with open(self._temp_db_file, "rb") as f:
                content = f.read()
                self._catalog_dict = pickle.loads(f.read()) if content else []

        if not self._catalog_dict:
            self._catalog_dict = BASE_JSON_DB

        self.select_all_items(reload=True)
        self.select_all_users()

    def insert_item(self, item: Item, commit=True) -> bool:
        parent = self.select_item_by_id(item.parent_id)

        if item.parent_id > 0:
            assert parent, "PARENT ITEM DOESN'T EXIST"
            assert not parent.children or item not in parent.children, \
                "ITEM ALREADY EXISTS IN THEN CHILDREN LIST OF PARENT ITEM"

        item.id = self.fetch_latest_item_id()
        self._item_dict[item.id] = item
        if item.parent_id > 0:
            parent.children.append(item)
            parent.type = "folder"
        if commit:
            self._store()
        return True

    def delete_item(self, item: Item, commit=True) -> bool:
        if not self.select_item_by_id(item.id):
            return True
        parent = self.select_item_by_id(item.parent_id)
        if item.parent_id > 0:
            assert parent, "PARENT ITEM DOESN'T EXIST"
            assert parent.children and item in parent.children, \
                "ITEM DOESN'T EXIST IN THE CHILDREN LIST OF PARENT ITEM"
            parent.children.remove(item)
            if not parent.children:
                parent.type = "file"

        self._item_dict.pop(item.id)
        if commit:
            self._store()
        return True

    def update_item(self, item: Item, commit=True) -> bool:
        if not self.select_item_by_id(item.id) and item.id > 0:
            raise Exception("THIS ITEM DOESN'T EXIST: <{}>".format(item.id))

        parent = self.select_item_by_id(item.parent_id)
        if item.parent_id > 0:
            assert parent, "PARENT ITEM DOESN'T EXIST"
        # no need to update the children list of parent item, as this item data is
        # synchronization between children list of parent item and self._item_dict.
        self._item_dict[item.id] = item
        if commit:
            self._store()
        return True

    def commit(self):
        self._store()

    def select_all_items(self, reload=False):
        if reload == False and self._item_dict is not None:
            return self._item_dict

        self._current_item_id = ITEM_ROOT_ID
        items_block = self._catalog_dict.get("items")
        if not items_block:
            return {}
        for block in items_block.values():
            item = self._json_block_to_item(block)
            if item.id > self._current_item_id:
                self._current_item_id = item.id
            self._item_dict[item.id] = item

        for parent in self._item_dict.values():
            for child in self._item_dict.values():
                if child.parent_id == parent.id:
                    parent.children.append(child)
        return self._item_dict

    def select_item_by_id(self, id):
        return self._item_dict.get(id)

    def select_items_by_parent_id(self, parent_id):
        items = []
        if parent_id == 0:
            for item in self._item_dict.values():
                if item.parent_id == 0:
                    items.append(item)
            return items

        parent = self.select_item_by_id(parent_id)
        assert parent, "Not Found the parent_id: <{}>".format(parent_id)
        return parent.children

    def select_items_by_title(self, title, like: bool = False):
        items = []
        if like:
            for item in self._item_dict:
                if item.title == title:
                    items.append(item)
        else:
            for item in self._item_dict:
                if re.match(item.title, title):
                    items.append(item)
        return items

    def fetch_catalog_for_font_end(self):
        items = self.select_items_by_parent_id(0)
        return json.loads(json.dumps(items, cls=JsonEncoderForFrontEnd))

    def _json_block_to_item(self, block):
        item = Item(
            title=block.get("title"),
            type=block.get("type"),
            parent_id=block.get("parent_id"),
            children=[],
            icon_path=block.get("ico_path"),
            file_path=block.get("file_path"),
            file_hash=block.get("file_hash"),
            status=block.get("status"),
            creation_time=block.get("creation_time"),
            modification_time=block.get("modification_time")
        )
        item.id = block.get("id")
        return item

    def _item_to_json_block(self, item):
        return {
            "id": item.id,
            "title": item.title,
            "parent_id": item.parent_id,
            "icon_path": item.icon_path,
            "file_path": item.file_path,
            "file_hash": item.file_hash,
            "status": item.status,
            "create_time": item.creation_time,
            "modification_time": item.modification_time
        }

    def _insert_lock_item_id(self, item_id):
        if not self.select_item_by_id(item_id):
            raise Exception("THE KEY DOESN'T EXIST: <{}>".format(item_id))
        if item_id not in self._catalog_dict["lock_item_ids"]:
            self._catalog_dict["lock_item_ids"].append(item_id)
        return True

    def _delete_lock_item_id(self, item_id):
        if not self.select_item_by_id(item_id):
            raise Exception("THE KEY DOESN'T EXIST: <{}>".format(item_id))
        if item_id in self._catalog_dict["lock_item_ids"]:
            self._catalog_dict["lock_item_ids"].remove(item_id)
        return True

    def select_all_users(self):
        users_block = self._catalog_dict.get("users")
        if not users_block:
            return []
        for block in users_block.values():
            user = User(
                username=block.get('username'),
                password=block.get('password'),
                regist_time=block.get('regist_time')
            )
            user.login_host = block.get('login_host')
            user.login_time = block.get('login_time')
            user.edit_item_id = block.get('edit_item_id')
            user.edit_start_time = block.get('edit_start_time')
            self._user_dict[user.username] = user
        return self._user_dict

    def select_user_by_username(self, username):
        return self._user_dict.get(username)

    def insert_user(self, user: User, commit=True):
        if self.select_user_by_username(user.username):
            raise Exception("USER ALREADY EXISTS: <{}>".format(user))
        self._user_dict[user.username] = user

        if commit:
            self._store()
        return True

    def update_user(self, user: User, commit=True):
        pre_user = self.select_user_by_username(user.username)
        if not pre_user:
            raise Exception("User not found: <{}>".format(user))
        self._user_dict[user.username] = user
        if pre_user.edit_item_id != user.edit_item_id:
            self._delete_lock_item_id(pre_user.edit_item_id)
            self._insert_lock_item_id(user.edit_item_id)

        if commit:
            self._store()
        return True

    def update_catalog_title(self, title):
        self._catalog_dict["title"] = title
        self._store()
        return True

    def select_catalog_title(self):
        return self._catalog_dict.get("title")

    def fetch_latest_item_id(self):
        with lock:
            self._current_item_id += 1
        return self._current_item_id

    def update_last_sync_sha(self, sha):
        self._catalog_dict["last_sync_sha"] = sha
        self._catalog_dict["last_sync_time"] = datetime.now()

    def _store(self):
        self._catalog_dict["modification_time"] = datetime.now()
        self._catalog_dict["version"] += 1
        self._catalog_dict["items"] = self._item_dict
        self._catalog_dict["users"] = self._user_dict

        try:
            with open(self.db_file, 'w', encoding="utf8") as f:
                content = json.dumps(self._catalog_dict,
                                     cls=JsonEncoderForPersistence,
                                     indent=4, sort_keys=True, ensure_ascii=False)
                f.write(content)
        except Exception as e:
            with open(self.db_file, 'wb') as f:
                f.write(pickle.dumps(self._catalog_dict))
            raise e
            # raise Exception("Failed to save catalog data, but write these to tempfile."
            #                 "Pelase resolve the malfunction before restarting this app")
        return True
