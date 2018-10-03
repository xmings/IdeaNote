#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/6
import os, shutil, mimetypes
from datetime import datetime
from config import BaseConfig
from model import Catalog, db
from git import Repo
from git.exc import InvalidGitRepositoryError

NOTES_DIRCTORY = BaseConfig.NOTES_DIRCTORY
REMOTE_URL = BaseConfig.REMOTE_URL



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
            path = NOTES_DIRCTORY

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
    filePath = ""
    if node.nodeType == 'folder':
        filePath = 'init'

    while node and node.fileName:
        filePath = os.path.join(node.fileName, filePath)
        node = node.parent

    filePath = os.path.join(NOTES_DIRCTORY, filePath.rstrip("\\") + ".md")
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
    path = genFilePath(node)
    if node.nodeType == 'file':
        try:
            os.remove(path)
        except Exception as e:
            print(e.args)
            return False
    else:
        path = os.path.dirname(path)
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
    imgFile = os.path.join(NOTES_DIRCTORY, path)
    imgType = mimetypes.guess_type(imgFile)[0]
    img = cat(imgFile, 'rb')
    return [img, imgType]

def saveImage(img, node):
    file = genFilePath(node)
    path = os.path.join(os.path.dirname(file), 'img')
    imgType = img.mimetype.split('/')[1]
    imgPath = os.path.join(path, '{}.{}'.format(fetchUniqName(), imgType))
    writeFile(imgPath, img, 'wb')
    src = os.path.relpath(imgPath, NOTES_DIRCTORY)
    return src

def writeFile(filePath, content, mode='w'):
    dir = os.path.dirname(filePath)
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)

        if mode=='wb':
            content.save(filePath)
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


class Sync(object):
    def __init__(self):
        self.local_repo = NOTES_DIRCTORY
        self.remote_url = REMOTE_URL
        self.init()

    def init(self, init=False):
        if not os.path.exists(self.local_repo):
            os.makedirs(self.local_repo)

        if init:
            self.repo = Repo.init(self.local_repo)
        else:
            try:
                self.repo = Repo(path=self.local_repo)
            except InvalidGitRepositoryError as e:
                shutil.rmtree(self.local_repo)
                os.mkdir(self.local_repo)
                self.repo = Repo.clone_from(self.remote_url, self.local_repo)

        self.remote = self.repo.remote()

    def get(self):
        try:
            self.remote.pull(refspec="master")
        except Exception as e:
            return False
        return True

    def put(self):
        try:
            self.repo.index.add("*")
            self.repo.index.commit("同步")
            self.remote.push(refspec="master")
        except Exception as e:
            return False
        return True

    def run(self):
        status = self.get()
        if status:
            status = self.put()
        return status




















