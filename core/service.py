#!/bin/python
# -*- coding: utf-8 -*-
# @File  : service.py
# @Author: wangms
# @Date  : 2019/5/9
# @Brief: 简述报表功能
from app import catalogdb

class CatalogService(object):
    def __init__(self):
        pass


    def fetch_all_items_to_json(self):
        catalog_tree = catalogdb.select_item_by_id(0)
        items = []
        for item in catalogdb.select_all_items():
            if item.id == 0:
                pass
            pass

