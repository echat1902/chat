from flask import request

from ..models import *


# 判断是否已经是好友
def chkfriend():
    pri_id = request.form['pri_id']
    sub_id = request.form['sub_id']

    re = db.session.query(Relation).filter_by(pri_id=pri_id,sub_id=sub_id).first()
    if re:
        return "已经是好友，不能重复添加"