#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/5/28
# @Brief: 简述报表功能
import os, shutil
from git import Repo
from git.exc import InvalidGitRepositoryError

class Sync(object):
    def __init__(self, app=None):
        self.local_repo = None
        self.remote_url = None
        if app:
            self.init_sync(app)

    def init_sync(self, app, init=False):
        self.local_repo = app.config.get("NOTES_DIRCTORY")
        self.remote_url = app.config.get("REMOTE_URL")
        if not os.path.exists(self.local_repo):
            os.makedirs(self.local_repo)

        if init:
            self.repo = Repo.init(self.local_repo)
        else:
            try:
                self.repo = Repo(path=self.local_repo)
            except InvalidGitRepositoryError as e:
                shutil.rmtree(self.local_repo)
                os.mkdir(self.local_repo)
                self.repo = Repo.clone_from(self.remote_url, self.local_repo)

        self.remote = self.repo.remote()

    def get(self):
        self.remote.pull(refspec="master")

    def put(self):
        self.repo.index.add("*")
        self.repo.index.commit("同步")
        self.remote.push(refspec="master")

    def run(self):
        self.get()
        self.put()
