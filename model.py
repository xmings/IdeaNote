#!/bin/python
# -*- coding: utf-8 -*-
# @File  : model.py
# @Author: wangms
# @Date  : 2018/8/6
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Catalog(db.Model):
    catalog_id = db.Column(db.Integer, primary_key=True)
    catalog_name = db.Column(db.String(100))
    catalog_type = db.Column(db.String(10))
    catalog_pid = db.Column(db.Integer)
    catalog_desc = db.Column(db.Text)
    catalog_img = db.Column(db.Binary)
    status = db.Column(db.String(2), nullable=False, default='Y')
    create_time = db.Column(db.DateTime, default=datetime.now())
    modify_time = db.Column(db.DateTime)

    parent = db.relationship('Catalog', remote_side=[catalog_id])

    def __repr__(self):
        return '<Catalog %r>' % self.catalog_name


class Article(db.Model):
    article_id = db.Column(db.Integer, primary_key=True)
    catalog_id = db.Column(db.Integer, nullable=False)
    article_title = db.Column(db.String(100))
    article_type = db.Column(db.String(10))
    article_img = db.Column(db.Binary)
    article_hash = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(2), nullable=False, default='Y')
    create_time = db.Column(db.DateTime, default=datetime.now())
    modify_time = db.Column(db.DateTime)

    catalog = db.relationship('Catalog', backref='articles', lazy=True)

    def __repr__(self):
        return '<Article %r>' % self.article_title


class Operation(db.Model):
    operation_id = db.Column(db.Integer, primary_key=True)
    sequence_no = db.Column(db.Integer)
    command = db.Column(db.String(200))
    status = db.Column(db.String(2), nullable=False, default='Y')
    create_time = db.Column(db.DateTime, default=datetime.now())
    modify_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Operation %r>' % self.command


