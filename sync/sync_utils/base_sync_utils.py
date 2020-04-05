#!/bin/python
# -*- coding: utf-8 -*-
# @File  : base_sync_utils.py
# @Author: wangms
# @Date  : 2019/12/19
# @Brief: 简述报表功能
from abc import ABC, abstractmethod


class BaseSyncUtils(ABC):
    @abstractmethod
    def is_online(self):
        pass

    @abstractmethod
    def init_version_info(self):
        pass

    @abstractmethod
    def load_version_info(self) -> dict:
        pass

    @abstractmethod
    def dump_version_info(self, version_info: dict) -> bool:
        pass

    @abstractmethod
    def load_note_info(self, version: int) -> dict:
        pass

    @abstractmethod
    def load_latest_note_info(self, note_id) -> dict:
        pass

    @abstractmethod
    def load_note_info_by_version_note_id(self,version, note_id) -> dict:
        pass

    @abstractmethod
    def dump_note_info(self, note_info: dict) -> bool:
        pass

    @abstractmethod
    def fetch_sync_note_list(self):
        pass

    @abstractmethod
    def delete_obsolete_change(self, day:int=30):
        pass
