#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/6/4


CONFIG = {
    "app_id": "02fa227d-1e50-47ea-83b0-f2abc939668e",
    "app_secret": "dynjNH43916);gkwOWLTT=-",
    "redirect": "http://localhost:8000/tutorial/callback",
    "scopes": "openid profile offline_access user.read calendars.read",
    "authority": "https://login.microsoftonline.com/common",
    "authorize_endpoint": "/oauth2/v2.0/authorize",
    "token_endpoint": "/oauth2/v2.0/token"

}

class Sync(object):
    pass
