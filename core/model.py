#!/bin/python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: wangms
# @Date  : 2019/7/31
from app import db
from datetime import datetime


class Catalog(db.Model):
    __tablename__ = "t_catalog"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    icon = db.Column(db.Binary)
    parent_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    content_sha = db.Column(db.String(100))
    seq_no = db.Column(db.Integer)
    status = db.Column(db.Integer, nullable=False, default=1)
    creation_time = db.Column(db.DateTime, default=datetime.now())
    modification_time = db.Column(db.DateTime)


class Image(db.Model):
    __tablename__ = "t_note_reference_image"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note_id = db.Column(db.Integer, db.ForeignKey('t_catalog.id'))
    status = db.Column(db.Integer, nullable=False, default=1)
    creation_time = db.Column(db.DateTime, default=datetime.now())
    modification_time = db.Column(db.DateTime)


class Snap(db.Model):
    __tablename__ = "t_content_snap"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note_id = db.Column(db.Integer, db.ForeignKey('t_catalog.id'))
    content = db.Column(db.Text)
    creation_time = db.Column(db.DateTime, default=datetime.now())
    modification_time = db.Column(db.DateTime)

class SyncRecord(db.Model):
    __tablename__ = "t_sync_log"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sync_sha = db.Column(db.String(100))
    creation_time = db.Column(db.DateTime, default=datetime.now())
    modification_time = db.Column(db.DateTime)
