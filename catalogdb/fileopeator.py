#!/bin/python
# -*- coding: utf-8 -*-
# @File  : fileopeator.py
# @Author: wangms
# @Date  : 2019/5/26
# @Brief: 简述报表功能
import os, shutil, mimetypes
from datetime import datetime

class FileOperator(object):
    def __init__(self, app=None):
        self.notes_directory = None
        self.image_folder = ".img"
        self.item_file_suffix = None
        self.folder_content_file = None
        if app:
            self.init_file(app)

    def init_file(self, app):
        self.notes_directory = app.config.get("NOTES_DIRCTORY")
        self.image_folder = app.config.get("IMAGE_FOLDER")
        self.item_file_suffix = app.config.get("ITEM_FILE_SUFFIX")
        self.folder_content_file = app.config.get("FOLDER_CONTENT_FILE")
        # create root .init.md
        root_init_md = self._combin_path(self.folder_content_file)
        if not os.path.isfile(root_init_md):
            self.write_file(root_init_md, "To write what you want")

    def create_folder(self, path: str):
        path = self._combin_path(path)
        assert os.path.isdir(os.path.dirname(path))
        os.mkdir(path)
        return True

    def rename_folder(self, path: str, title: str):
        path = self._combin_path(path)
        assert os.path.isdir(path)
        new_path = os.path.join(os.path.dirname(path), title)
        os.rename(path, new_path)
        return True

    def move_floder(self, src, dst):
        src = self._combin_path(src)
        dst = self._combin_path(dst)
        assert os.path.isdir(src)
        assert os.path.isdir(dst)
        shutil.move(src, dst)
        return True

    def delete_folder(self, path):
        path = self._combin_path(path)
        if os.path.isabs(path):
            os.removedirs(path)
        return True

    def read_file(self, path: str):
        path = self._combin_path(path)
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf8") as f:
            return f.read()

    def write_file(self, path, content):
        path = self._combin_path(path)
        assert os.path.isdir(os.path.dirname(path))
        with open(path, "w", encoding="utf8") as f:
            f.write(content)
        return True

    def rename_file(self, path, title):
        path = self._combin_path(path)
        assert os.path.isfile(path)
        new_path = os.path.join(os.path.dirname(path), "{}{}".format(title, self.item_file_suffix))
        os.rename(path, new_path)
        return True

    def move_file(self, src, dst):
        # dst is a file or a folder
        src = self._combin_path(src)
        dst = self._combin_path(dst)
        assert os.path.isfile(src)
        assert os.path.isdir(dst) or os.path.isdir(os.path.dirname(dst))
        return shutil.move(src, dst)

    def delete_file(self, path):
        path = self._combin_path(path)
        if os.path.isfile(path):
            os.remove(path)
        return True

    def read_image(self, item_path, image_name):
        file_abs_path = self._combin_path(item_path)
        assert os.path.isfile(file_abs_path)
        image_abs_path = self._combin_path(os.path.dirname(item_path),
                                           self.image_folder, image_name)
        with open(image_abs_path, "rb") as f:
            return f.read(),mimetypes.guess_type(image_abs_path)[0]

    def write_image(self, item_path, image, mime_type):
        file_abs_path = self._combin_path(item_path)
        image_dir_path = os.path.join(os.path.dirname(file_abs_path), self.image_folder)
        if not os.path.isdir(image_dir_path):
            self.create_folder(image_dir_path)
        suffix = image.content_type.split("/")[1]
        image_name = "{}.{}".format(FileOperator.fetch_uniq_name(), suffix)

        with open(os.path.join(image_dir_path, image_name), "wb") as f:
            image.save(f)
        return image_name

    def delete_image(self, item_path, image_name):
        file_abs_path = self._combin_path(item_path)
        assert os.path.isfile(file_abs_path)
        image_abs_path = self._combin_path(os.path.dirname(item_path), self.image_folder, image_name)

        if os.path.isfile(image_abs_path):
            os.remove(image_abs_path)
        return True

    def move_image(self, src, dst):
        src = self._combin_path(src)
        dst = self._combin_path(dst)
        assert os.path.isfile(src)
        assert os.path.isdir(dst)
        shutil.move(src, dst)
        return True

    def _combin_path(self, path: str, *args):
        if os.path.isabs(path):
            assert path.startswith(self.notes_directory)
            return os.path.join(path, *args) if args else path
        return os.path.join(self.notes_directory, path, *args) \
            if args else os.path.join(self.notes_directory, path)

    def is_file(self, path: str):
        return os.path.isfile(self._combin_path(path))

    def is_folder(self, path: str):
        return os.path.isdir(self._combin_path(path))

    @classmethod
    def fetch_uniq_name(precision='s'):
        if precision == 'ms':
            return datetime.now().strftime('%Y%m%d%H%M%S%f')
        return datetime.now().strftime('%Y%m%d%H%M%S')


