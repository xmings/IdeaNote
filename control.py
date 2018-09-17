#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/6
import os, shutil, mimetypes
from datetime import datetime
from config import BaseConfig
from model import Catalog, db

def fetchUniqName(precision='s'):
    if precision == 'ms':
        return datetime.now().strftime('%Y%m%d%H%M%S%f')
    return datetime.now().strftime('%Y%m%d%H%M%S')

def nodes2Json(nodes):
    start = Catalog.query.filter(Catalog.parent == None).first()
    catalog = _nodes2Json(nodes, start, {
        "id:": "",
        "name": "root",
        "open": False,
        "children": []
    })
    return str(catalog).replace("'", '"')


def _nodes2Json(nodes, node, block):
    childrens = Catalog.query.filter(Catalog.parent == node).all()
    for c in childrens:
        block["children"].append({
            "label": c.step_name,
            "children": []
        })
        _nodes2Json(nodes, c, block["children"][-1])
    return block


class Table2Json(object):

    def __init__(self):
        self.json = []
        self.block = ''
        self.nodePid = ''

    def run(self):
        nodes = Catalog.query.order_by(Catalog.level).all()
        for n in nodes:
            if not n.nodePid:
                self.json.append({
                    "id": n.nodeId,
                    "name": n.nodeTitle,
                    "open": n.nodeType == 'folder',
                    "childen": []
                })
            else:
                self.addNode(n, self.json)

        if not self.json:
            self.initCatalog()
            self.run()
        return self.json

    def addNode(self, node, jblocks):
        for block in jblocks:
            if block["id"] == node.nodePid:
                if not block.get("children"):
                    block["children"] = []
                block["children"].append({
                    "id": node.nodeId,
                    "name": node.nodeTitle,
                    "open": False
                })
                return True
            elif block.get("children"):
                self.addNode(node, block["children"])

    def initCatalog(self, path=None):
        if not path:
            path = BaseConfig.NOTES_DIRCTORY

        if not os.path.exists(path):
            os.makedirs(path)

        # 初始化根节点init.md文件
        file = os.path.join(path, 'init.md')
        writeFile(file, '## 欢迎使用IdeaNote ##')

        root = Catalog(
            nodeTitle='Mybase',
            nodeType='folder',
            fileName=path,
            level=0,
            status=1,
            createTime=datetime.now()
        )
        db.session.add(root)
        db.session.commit()


def genFilePath(node):
    if node.nodeType == 'folder':
        filePath = "init.md"
    else:
        filePath = node.fileName + ".md"

    while node and node.fileName:
        filePath = os.path.join(node.fileName, filePath)
        node = node.parent

    # filePath = os.path.join(BaseConfig.PROJECT_PATH, filePath)
    return filePath

def changeFile2Folder(node):
    filePath = genFilePath(node)
    try:
        folderPath = filePath.rstrip('.md')
        os.mkdir(folderPath)
        newFile = os.path.join(folderPath, 'init.md')
        shutil.move(filePath, newFile)
    except Exception as e:
        print(e.args)
        return False
    return True

def dropNodeWithChildren(node):
    children = Catalog.query.filter_by(nodePid=node.nodeId).all()
    for c in children:
        child = Catalog.query.filter_by(nodePid=c.nodeId).first()
        if child:
            dropNodeWithChildren(c)
        else:
            db.session.delete(c)
            db.session.commit()
    db.session.delete(node)
    db.session.commit()

def dropDirWithChildren(node):
    if node.nodeType == 'file':
        path = genFilePath(node)
    else:
        path = os.path.dirname(genFilePath(node))
    try:
        shutil.rmtree(path)
    except Exception as e:
        print(e.args)
        return False
    return True

def moveDirWithChildren(node, pnode):
    nodeFile = genFilePath(node)
    pnodeFile = genFilePath(pnode)
    try:
        currDir = os.path.dirname(nodeFile)
        targetDir = os.path.dirname(pnodeFile)
        shutil.move(currDir, targetDir)
    except Exception as e:
        print(e.args)
        return False
    return True

def readContent(node):
    filePath = genFilePath(node)
    content = cat(filePath, 'r')
    return content

def saveContent(node, content):
    filePath = genFilePath(node)
    status = writeFile(filePath, content)
    return status

def readImage(path):
    imgFile = '{}/{}'.format(BaseConfig.PROJECT_PATH, path)
    imgType = mimetypes.guess_type(imgFile)[0]
    img = cat(imgFile, 'rb')
    return [img, imgType]

def saveImage(img, node):
    file = genFilePath(node)
    path = os.path.join(os.path.dirname(file), 'img')
    imgType = img.mimetype.split('/')[1]
    imgPath = os.path.join(path, '{}.{}'.format(fetchUniqName(), imgType))
    writeFile(imgPath, img, 'wb')
    src = os.path.relpath(imgPath, BaseConfig.PROJECT_PATH)
    return src

def writeFile(filePath, content='', mode='w'):
    dir = os.path.dirname(filePath)
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)

        if mode=='wb':
            with open(filePath, mode) as f:
                f.write(content)
        else:
            with open(filePath, mode, encoding='utf8') as f:
                f.write(content)
    except Exception as e:
        print(e.args)
        return False
    return True

def cat(filePath, mode='r'):
    content = '' if mode=='r' else b''
    if os.path.exists(filePath):
        try:
            if mode == 'rb':
                with open(filePath, mode) as f:
                    content = f.read()
            else:
                with open(filePath, mode, encoding='utf8') as f:
                    content = f.read()
        except Exception as e:
            print(e.args)
    else:
        writeFile(filePath, content, mode)
    return content







