#!/bin/python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: wangms
# @Date  : 2018/8/6
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Catalog(db.Model):
    __tablename__ = 't_catalog'
    nodeId = db.Column('node_id', db.Integer, primary_key=True)
    nodeTitle = db.Column('node_title', db.String(100))
    nodeType = db.Column('node_type', db.String(10))
    nodePid = db.Column('node_pid', db.Integer, db.ForeignKey('t_catalog.node_id'))
    nodeImg = db.Column('node_img', db.Binary)
    fileName = db.Column('file_name', db.String(100), unique=True)
    fileHash = db.Column('file_hash', db.String(100))
    level = db.Column('level', db.Integer)
    status = db.Column('status', db.String(2), nullable=False, default=1)
    createTime = db.Column('create_time', db.DateTime, default=datetime.now())
    modifyTime = db.Column('modify_time', db.DateTime)

    parent = db.relationship('Catalog', remote_side=[nodeId])

    def __repr__(self):
        return '<Catalog %r>' % self.nodeTitle


class Operation(db.Model):
    operId = db.Column('oper_id', db.Integer, primary_key=True)
    seqNo = db.Column('seq_no', db.Integer)
    command = db.Column('command', db.String(200))
    status = db.Column('status', db.String(2), nullable=False, default='Y')
    createTime = db.Column('create_time', db.DateTime, default=datetime.now())
    modifyTime = db.Column('modify_time', db.DateTime)

    def __repr__(self):
        return '<Operation %r>' % self.command


