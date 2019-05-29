"""
群信息展示与修改功能
"""
import json

from flask import request

from app.zsg import zsg


@zsg.route('/group_info', methods=['POST'])
def group_info():
    """
    修改群信息
    :return:
    """
    pass


@zsg.route('/group_head_upload', methods=['POST'])
def group_head_upload():
    """
    上传群头像
    :return:
    """

    # 获取前端发送的json数据
    data = json.loads(request.form.get('data'))
    # 从json数据中获取群信息

    # 保存图片
    # 修改数据库
    # 返回消息
    pass
