#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2018/8/6
from datetime import datetime
from . import core
from flask import render_template, request, jsonify
from app import db
from model import Catalog
from control import Table2Json, dropChildren, \
    genFilePath, changeFile2Folder, writeContent, readContent


@core.route('/')
def index():
    return render_template('editor.html')

@core.route('/node/',methods=['GET'])
def getNodes():
    nodes = Catalog.query.order_by(Catalog.level).all()
    t2j = Table2Json()
    jNodes = t2j.run(nodes)
    return jsonify(jNodes)


@core.route('/node/<nodeId>',methods=['GET'])
def getNode(nodeId):
    node = Catalog.query.filter_by(nodeId=nodeId).first()
    return readContent(node)


@core.route('/node/add', methods=['POST'])
def addNode():
    info = {
        'nodeTitle': request.form.get('nodeTitle'),
        'nodePid': request.form.get('nodePid'),
        'nodeType': 'file',
        'fileName': datetime.now().strftime('%Y%m%d%H%M%S')
    }
    pnode = Catalog.query.filter_by(nodeId=info['nodePid']).first()
    status = changeFile2Folder(pnode)
    if not status:
        return 'error', 500
    if pnode.nodeType == 'file':
        pnode.nodeType = 'folder'
    info['level'] = pnode.level + 1
    node = Catalog(**info)
    db.session.add(node)
    db.session.commit()
    writeContent(node, '')
    return jsonify({"nodeId": node.nodeId })


@core.route('/node/update/<type>', methods=['POST'])
def updateNode(type):
    nodeId = request.form.get('nodeId')
    node = Catalog.query.filter_by(nodeId=nodeId).first()
    if type == "rename":
        node.nodeTitle = request.form.get('nodeTitle')
    elif type == "position":
        node.nodePid = request.form.get('nodePid')
    elif type == "content":
        content = request.form.get('content')
        status = writeContent(node, content)
        if not status:
            return 'error', 500
    else:
        node.nodeImg = request.form.get('nodeImg')
        node.status = request.form.get('status')
    db.session.commit()
    return 'OK', 200


@core.route('/node/drop', methods=['POST'])
def dropNode():
    nodeId = request.form.get('nodeId')
    node = Catalog.query.filter_by(nodeId=nodeId).first()
    dropChildren(node)
    db.session.delete(node)
    db.session.commit()
    return 'OK', 200

