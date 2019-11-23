#!/bin/python
# -*- coding: utf-8 -*-
# @File  : Listener.py
# @Author: wangms
# @Date  : 2019/11/16
import os
import shutil
import logging
from urlmark.location import fetch_bookmark_info
from datetime import datetime, timedelta
from common import conf
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Lock
"""
"""

class ChromeBookmarkListener(object):
    def __init__(self):
        self.bm_file_info = fetch_bookmark_info("Chrome")
        self.local_file = self.bm_file_info.get("bookmark_file_path")
        assert conf.urlmark_sync, "请先在config.yml中配置urlmark=True已开启Chrome浏览器书签同步"
        if not os.path.exists(conf.urlmark_file):
            shutil.copyfile(self.local_file, conf.urlmark_file)
        self.event_handler = SyncBookmarkEventHandler(self.local_file, conf.urlmark_file)


    def listen_local(self):
        observer = Observer()
        observer.schedule(self.event_handler, self.local_file)
        observer.start()
        return observer

    def listen_server(self):
        observer = Observer()
        observer.schedule(self.event_handler, conf.urlmark_file)
        observer.start()
        return observer


class SyncBookmarkEventHandler(FileSystemEventHandler):
    def __init__(self, local_file, server_file):
        self.local_file = local_file
        self.server_file = server_file
        self.lock = Lock()
        self.last_sync_time = None

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    def on_modified(self, event):
        super().on_modified(event)

        with self.lock:
            logging.info(f"{event.src_path} {event.event_type}")
            if datetime.now() - self.last_sync_time < timedelta(seconds=2):
                return

            if event.src_path == self.server_file:
                shutil.copyfile(conf.urlmark_file, self.local_file)

            else:
                shutil.copyfile(self.local_file, conf.urlmark_file)

            self.last_sync_time = datetime.now()


if __name__ == '__main__':
    sync = ChromeBookmarkListener()
    local = sync.listen_local()
    server = sync.listen_server()
    local.join()
    server.join()