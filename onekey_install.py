#!/bin/python
# -*- coding: utf-8 -*-
# @File  : onekey_install.py.py
# @Author: wangms
# @Date  : 2019/11/14
import logging
import sqlalchemy
import os
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.info("==========初始化IdeaNote开始===========")

current_dir = os.path.dirname(os.path.abspath(__file__))

logger.info("1. 安装依赖包")
import platform
requirements_file = os.path.join(current_dir, "requirements.txt")
with open(requirements_file, "r", encoding="utf8") as f:
    requirements = [i.strip() for i in f.readlines()]
if platform.system() == "Windows":
    requirements.append("pypiwin32-223")

import subprocess
completed = subprocess.run(f"pip install {' '.join(requirements)}", shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")
logger.info(completed.stdout)
if completed.returncode != 0:
    logger.error(completed.stderr)
    sys.exit(1)
logger.info("    通过！\n")


logger.info("2. 检查配置文件")
config_file = os.path.join(current_dir, "config.yml")
if not os.path.exists(config_file):
    logger.error(f"\033[1;31m {config_file}文件不存在， 请复制config.sample.yml为config.yml，并修改其中的必要配置信息 \033[0m")
    sys.exit(1)
logger.info("    通过！\n")

from common import conf
logger.info("3. 检查同步目录")
if not os.path.exists(conf.sync_work_dir):
    logger.error("\033[1;31m 请在config.yml文件中正确指定work_dir的路径 \033[0m")
    sys.exit(1)
import json
with open(os.path.join(conf.sync_work_dir, "sync.metadata"), "w", encoding="utf8") as f:
    f.write(json.dumps({
            "writing_node": "",
            "sync_timestamp": {},
            "sync_version": {},
            "last_update_timestamp": None
    }, ensure_ascii=False, indent=4))
logger.info("    通过！\n")

logger.info("4. 检查日志目录")
if not os.path.exists(conf.log_directory):
    logger.error("\033[1;31m 请在config.yml文件中正确指定log_directory的路径 \033[0m")
    sys.exit(1)
logger.info("    通过！\n")

logger.info("5. 初始化DB")
from core.model import Catalog, Image, SyncRecord, Snap

db_file = conf.db_config.get("SQLALCHEMY_DATABASE_URI")
db = sqlalchemy.create_engine(db_file)
for t in [Catalog, Image, SyncRecord, Snap]:
    t.metadata.create_all(db.engine)
logger.info("    完成！\n")

logger.info("6. 启动IdeaNote")
from app import app
app.run(port=conf.app_port, threaded=True)
