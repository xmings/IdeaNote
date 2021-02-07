#!/bin/python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: wangms
# @Date  : 2019/12/18

from app import db


class SyncInfo(db.Model):
    __tablename__ = "t_sync_info"
    id = db.Column(db.Integer, primary_key=True)
    current_version = db.Column(db.Integer)
    latest_version = db.Column(db.Integer)
    modification_time = db.Column(db.DateTime)
