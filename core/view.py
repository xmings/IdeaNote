#!/bin/python
# -*- coding: utf-8 -*-
# @File  : view.py
# @Author: wangms
# @Date  : 2018/8/6
from . import core
from flask import render_template, request, Response, jsonify
from app import db
from model import Catalog
from control import Table2Json, dropChildren, fetchUniqName, \
    genFilePath, changeFile2Folder, writeContent, readContent, saveImage, readImage


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
        'fileName': fetchUniqName()
    }
    pnode = Catalog.query.filter_by(nodeId=info['nodePid']).first()
    if pnode.nodeType == 'file':
        status = changeFile2Folder(pnode)
        if not status:
            return 'error', 500
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
    if node.level == 0:
        return 'FORBIDDEN', 403
    dropChildren(node)
    db.session.delete(node)
    db.session.commit()
    return 'OK', 200


@core.route('/node/upload', methods=['POST'])
def uploadImage():
    img = request.files.get('file')
    nodeId = request.form.get('nodeId')
    node = Catalog.query.filter_by(nodeId=nodeId).first()
    path = saveImage(img, node)

    return jsonify({'filename': path.replace('\\','/')}), 200

@core.route('/<path:imgPath>')
def getImage(imgPath):
    result = readImage(imgPath)
    if result:
        img, imgType = result
        resp = Response(img, mimetype=imgType)
        return resp
    return 'FORBIDDEN', 403

