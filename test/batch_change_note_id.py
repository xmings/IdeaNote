#!/bin/python
# -*- coding: utf-8 -*-
# @File  : batch_change_note_id.py
# @Author: wangms
# @Date  : 2019/8/2

from core.model import Catalog, db
from uuid import uuid1

def change_note_id():
    for n in Catalog.query.all():
        n.id = uuid1().hex
    db.session.commit()

    for n in Catalog.query.all():
        pn = Catalog.query.filter_by(sha=n.parent_id).first()
        n.parent_id = getattr(pn, "id") if hasattr(pn, "id") else None

    db.session.commit()

if __name__ == '__main__':
    change_note_id()