#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/6
import os, shutil
from config import BaseConfig
from model import Catalog, db



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

    def run(self, nodes):
        for n in nodes:
            if not n.nodePid:
                self.json.append({
                    "id": n.nodeId,
                    "name": n.nodeTitle,
                    "open": n.nodeType == 'folder',
                    "children": []
                })
            else:
                self.addNode(n, self.json)
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

def genFilePath(node):
    if node.nodeType == 'folder':
        filePath = "init.md"
    else:
        filePath = node.fileName + ".md"

    while node.parent and node.parent.fileName:
        filePath = os.path.join(node.parent.fileName, filePath)
        node = node.parent

    filePath = os.path.join(BaseConfig.NOTES_DIRCTORY, filePath)
    return filePath

def changeFile2Folder(node):
    filePath = genFilePath(node)
    try:
        folderPath = filePath.rstrip('.md')
        os.mkdir(folderPath)
        newFile = os.path.join(os.path.dirname(filePath), 'init.md')
        shutil.move(filePath, newFile)
    except Exception as e:
        print(e.args)
        return False
    return True

def dropChildren(node):
    children = Catalog.query.filter_by(nodePid=node.nodeId).all()
    for c in children:
        child = Catalog.query.filter_by(nodePid=c.nodeId).first()
        if child:
            dropChildren(c)
        else:
            db.session.delete(c)
            db.session.commit()

def writeContent(node, content):
    filePath = genFilePath(node)
    try:
        with open(filePath, 'w', encoding='utf8') as f:
            f.write(content)
    except Exception as e:
        print(e.args)
        return False
    return True

def readContent(node):
    filePath = genFilePath(node)
    content = ''
    try:
        with open(filePath, 'r', encoding='utf8') as f:
            content = f.read()
    except FileNotFoundError:
        writeContent(node, '')
    except Exception as e:
        print(e.args)
    return content

