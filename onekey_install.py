#!/bin/python
# -*- coding: utf-8 -*-
# @File  : onekey_install.py.py
# @Author: wangms
# @Date  : 2019/11/14
import logging
import os
import sys
from colorama import init as cmd_color_init, Fore, Back


welcome = """# 欢迎使用IdeaNote - 助你打造自己的知识平台
============
使用技巧：
- 右键`MyNote`即可创建新笔记
- 通过鼠标拖拽或者上下左右方向键可以调整笔记的位置
- 通过CTRL + i 进入文章编辑模式
- 通过ESC返回阅读模式
- 通过Shift + s 切换目录管理窗口
- 拖动窗口分界线可以调整各个窗口的大小
- 编辑窗口还可以直接粘贴图片哦

> 如在使用过程中有任何奇思妙想都可以在Github上发起issue，同时也期待你加入我们的开发团队。
"""
logging.getLogger(name="IdeaNoteSync").disabled = True

cmd_color_init(autoreset=True)

print(Fore.RED + "注意：该脚本是IdeaNote的初始化安装脚本，一旦继续会清除IdeaNote的笔记数据!!")
v = input("是否需要继续（Y：继续，N：退出）：")
if v.upper() != "Y":
    sys.exit(0)

current_dir = os.path.dirname(os.path.abspath(__file__))

print("1. 安装依赖包")

import platform
requirements_file = os.path.join(current_dir, "requirements.txt")
with open(requirements_file, "r", encoding="utf8") as f:
    requirements = [i.strip() for i in f.readlines()]
if platform.system() != "Windows":
    requirements.remove("pywin32")

import subprocess
for line in requirements:
    print(f"安装{line}")
    completed = subprocess.run(f"pip install {line}", shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, encoding="utf8")
if completed.returncode != 0:
    print(Fore.RED + completed.stderr)
    sys.exit(1)
print(">>>>>>完成！\n")

print("2. 检查配置文件")
config_file = os.path.join(current_dir, "config.yml")
if not os.path.exists(config_file):
    print(Fore.RED + f"{config_file}文件不存在， 请复制config.sample.yml为config.yml，并修改其中的必要配置信息")
    sys.exit(1)
print(">>>>>>通过！\n")

from common import conf
print("3. 初始化同步目录")
if conf.sync_method == "github":
    from sync.sync_utils.github_sync_utils import GithubSyncUtils
    GithubSyncUtils(conf.sync_connection_info).init_version_info()
elif conf.sync_method == "netdisk":
    from sync.sync_utils.netdisk_sync_utils import NetDiskSyncUtils
    NetDiskSyncUtils(conf.sync_work_dir).init_version_info()
else:
    print(Fore.RED + "错误的同步方式配置，请正确填写config.yml中的sync_method的值")
    sys.exit(1)

print(">>>>>>通过！\n")

print("4. 检查日志目录")
if not os.path.exists(conf.log_directory):
    print(Fore.RED + "请在config.yml文件中正确指定log_directory的路径")
    sys.exit(1)
print(">>>>>>通过！\n")

print("5. 初始化DB")
import zlib
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from core.model import Catalog, Image, SyncRecord
from sync.model import SyncInfo


db_file = conf.db_config.get("SQLALCHEMY_DATABASE_URI")
db = sqlalchemy.create_engine(db_file)
session = sessionmaker(bind=db)()
for t in [Catalog, Image, SyncRecord, SyncInfo]:
    t.metadata.drop_all(db.engine)
    t.metadata.create_all(db.engine)
root_node = Catalog(title="MyNote", parent_id="self", content=zlib.compress(welcome.encode("utf8")), status=1)
session.add(root_node)
sync_init = SyncInfo(current_version=0, latest_version=0)
session.add(sync_init)
session.commit()
print(">>>>>>完成！\n")
print("安装成功，手工执行以下命令启动IdeaNote:")
print(Fore.GREEN + f"python {os.path.join(current_dir, 'app.py')} ")


input("回车退出...\n")

