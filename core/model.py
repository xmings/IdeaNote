#!/bin/python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: wangms
# @Date  : 2019/7/31
from app import db
from uuid import uuid1
from datetime import datetime


class Catalog(db.Model):
    __tablename__ = "t_catalog"
    id = db.Column(db.String, primary_key=True, default=lambda: uuid1().hex)
    title = db.Column(db.String(100))
    icon = db.Column(db.Binary)
    parent_id = db.Column(db.String)
    content = db.Column(db.Binary)
    remote_content = db.Column(db.Binary)
    seq_no = db.Column(db.Integer, autoincrement=True)
    status = db.Column(db.Integer, default=1)
    creation_time = db.Column(db.DateTime, default=datetime.now())
    modification_time = db.Column(db.DateTime)
    change_time = max(creation_time, modification_time)


class Image(db.Model):
    __tablename__ = "t_note_reference_image"
    id = db.Column(db.String, primary_key=True, default=lambda: uuid1().hex)
    note_id = db.Column(db.String, db.ForeignKey('t_catalog.id'))
    image = db.Column(db.Binary)
    mime_type = db.Column(db.String)
    status = db.Column(db.Integer, default=1)
    creation_time = db.Column(db.DateTime, default=datetime.now())
    modification_time = db.Column(db.DateTime)
    change_time = max(creation_time, modification_time)


class Snap(db.Model):
    __tablename__ = "t_content_snap"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note_id = db.Column(db.String, db.ForeignKey('t_catalog.id'))
    content = db.Column(db.Text)
    creation_time = db.Column(db.DateTime, default=datetime.now())
    modification_time = db.Column(db.DateTime)

class SyncRecord(db.Model):
    __tablename__ = "t_sync_log"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sync_sha = db.Column(db.String(100))
    creation_time = db.Column(db.DateTime, default=datetime.now())
    modification_time = db.Column(db.DateTime)
