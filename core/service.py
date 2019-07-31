#!/bin/python
# -*- coding: utf-8 -*-
# @File  : service.py
# @Author: wangms
# @Date  : 2019/5/9
# @Brief: 简述报表功能
import os, mimetypes
from catalogdb import DBOperator, FileOperator, Item
from common import Result
from sync.git import Sync
from sync.github_sync import GithubSync
from flask import current_app

db_operator = DBOperator()
file_operator = FileOperator()
sync_operator = Sync()

"""
    This Catalog Service is SOA
"""
class NoteService(object):
    def __init__(self):
        self.root_item = None

    def fetch_all_items_to_json(self):
        children = db_operator.fetch_catalog_for_font_end()
        nodes = [
            {
                "id": 0,
                "name": db_operator.select_catalog_title(),
                "open": True,
                "children": children if isinstance(children, list) else [children]
            }
        ]
        return nodes

    def fetch_item_by_id(self, id: int):
        if int(id) == 0:
            if not self.root_item:
                self.root_item = Item(
                    id=0,
                    parent_id=0,
                    type="folder",
                    title=db_operator.select_catalog_title()
                )
                self.root_item.children = db_operator.select_items_by_parent_id(0)
            return self.root_item
        item = db_operator.select_item_by_id(int(id))
        assert item, "THIS ITEM DOESN'T EXISTS"
        return item

    def add_item(self, title: str, pid: int):
        parent = self.fetch_item_by_id(int(pid))
        parent_type = parent.type
        parent_path = self._auto_complete_path(parent.id)
        new_parent_dir = self._auto_complete_path(parent.id, auto=False)
        item = Item(title=title, parent_id=parent.id)
        db_operator.insert_item(item)
        item_path = self._auto_complete_path(item.id)
        if parent_type == "file":
            # create parent folder
            try:
                # create parent folder if parent is a file before
                file_operator.create_folder(new_parent_dir)
                # create item file
                file_operator.write_file(item_path, "")
                # move and rename the parent item file
                new_parent_path = self._auto_complete_path(parent.id)
                file_operator.move_file(parent_path, new_parent_path)
            except Exception as e:
                # rollback
                db_operator.delete_item(item)
                file_operator.delete_folder(parent_path)
                raise e
        else:
            # create item file
            try:
                assert not file_operator.is_file(item_path), \
                    "File already exists: <{}>".format(item_path)
                file_operator.write_file(item_path, "")
            except Exception as e:
                db_operator.delete_item(item)
                raise e

        return item

    def drop_item(self, id):
        if int(id) <= 0:
            return False

        item = self.fetch_item_by_id(int(id))
        item_path = self._auto_complete_path(item.id, auto=False)
        item_type = item.type
        parent = self.fetch_item_by_id(item.parent_id)
        parent_content_file = self._auto_complete_path(parent.id)
        parent_path = self._auto_complete_path(parent.id, auto=False)
        grandfather_path = self._auto_complete_path(parent.parent_id, auto=False)

        # if there is any item from this item children is a folder,
        # then refuse to drop this item.
        for child in item.children:
            assert not child.children, \
                "There are one or more folders under this item: {}".format(item_path)

        # first, we attempt to delete all children
        for child in item.children:
            file_path = self._auto_complete_path(child.id)
            file_operator.delete_file(file_path)
            db_operator.delete_item(child)

        # then, drop this item and corresponding folder
        if item_type == "file":
            file_operator.delete_file(item_path)
        else:
            file_operator.delete_folder(item_path)
        db_operator.delete_item(item)

        # lastly, if the children list of parent item is empty
        # after deleted the item as mentioned above,
        # in brief, we need to change the folder to a file.
        # note: permit to delete root item.
        if parent.id <= 0:
            return True

        if not parent.children:
            item_file = os.path.join(grandfather_path,
                                     "{}{}".format(parent.title, file_operator.item_file_suffix))
            file_operator.move_file(parent_content_file, item_file)
            file_operator.delete_folder(parent_path)

        return True

    def update_item_title(self, id, title):
        item = self.fetch_item_by_id(int(id))
        try:
            if item.type == "folder":
                file_path = self._auto_complete_path(item.id, auto=False)
                file_operator.rename_folder(file_path, title)
            else:
                file_path = self._auto_complete_path(item.id)
                file_operator.rename_file(file_path, title)

            item.title = title
            db_operator.update_item(item)
        except Exception as e:
            current_app.logger.error(e)
            return Result(False, e)

        return Result(True)

    def read_item_content(self, id):
        item = self.fetch_item_by_id(int(id))
        file_path = self._auto_complete_path(item.id)
        return file_operator.read_file(file_path)

    def update_item_content(self, id, content):
        try:
            item = self.fetch_item_by_id(int(id))
            file_path = self._auto_complete_path(item.id)
            file_operator.write_file(file_path, content)
        except Exception as e:
            current_app.logger.error(e)
            return Result(False, e)
        return Result(True)

    def read_item_image(self, id, image_name):
        item = self.fetch_item_by_id(int(id))
        item_path = self._auto_complete_path(item.id)
        return file_operator.read_image(item_path, image_name)

    def write_item_image(self, id, image):
        item = self.fetch_item_by_id(int(id))
        item_path = self._auto_complete_path(item.id)
        image_name = file_operator.write_image(item_path, image, image)
        return "/{}/{}".format(item.id, image_name)

    def note_push(self):
        try:
            sync_operator.put()
        except Exception as e:
            current_app.logger.error(e)
            return False
        return True

    def note_pull(self):
        try:
            sync_operator.get()
        except Exception as e:
            current_app.logger.error(e)
            return False
        return True

    def note_sync(self):
        try:
            sync_operator.run()
        except Exception as e:
            current_app.logger.error(e)
            return False
        return True


    def sync(self):
        # GithubSync()
        pass

    def _auto_complete_path(self, id: int, auto=True):
        path = ''
        item = self.fetch_item_by_id(int(id))
        while item.id > 0:
            path = os.path.join(item.title, path) if path else item.title
            item = self.fetch_item_by_id(item.parent_id)

        if not auto:
            return path
        # need to reload this item
        item = self.fetch_item_by_id(int(id))
        if item.type == "folder":
            return os.path.join(path, file_operator.folder_content_file)
        return "{}{}".format(path, file_operator.item_file_suffix)


