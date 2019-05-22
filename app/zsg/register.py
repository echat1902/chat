"""
用户注册模块
包含注册视图函数
生成user_no函数
user_pwd加密函数
"""

import datetime
import hashlib
import random
import uuid

from flask import render_template, request

from app import db
from app.common.funs import ret_sucess, ret_error, get_time
from app.zsg.form_check import FormCheck
from . import zsg
from ..models import User


@zsg.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册视图函数
    :return: get reg.html
             post 错误信息/自动登录
    """

    if request.method == "GET":
        return render_template('reg.html')
    else:
        # 从表单中获取用户名和密码，并校验
        user_name = request.form['user_name']
        res = FormCheck.name_check(user_name)
        if res != True:
            return ret_error(res)

        user_pwd = request.form['user_pwd']
        res = FormCheck.pwd_check(user_pwd)
        if res != True:
            return ret_error(res)

        user_pwd_confirm = request.form['user_rpwd']
        if user_pwd != user_pwd_confirm:
            # 把错误信息返回给前端
            return ret_error("两次密码不一致")

        # 创建user实体
        user = User()
        user.user_no = gen_user_no()
        user.user_nick_name = user_name
        user.user_pwd = gen_user_pwd(user_pwd)
        user.pic_name = "untitled.jpg"
        user.add_time = get_time()

        # 向数据库中插入数据
        try:
            db.session.add(user)
        except Exception as e_db_create:
            # 插入用户数据异常
            # 保存请求相关的信息和异常信息到日志文件中
            # 暂不实现，暂时打印到服务端控制台中
            print(e_db_create)
            # 把错误信息返回给前端
            return ret_error("该用户名已存在")
        else:
            # 手动提交，注册中的自动登录部分需要从数据库中查找数据
            db.session.commit()

        # 把成功信息返回给前端
        return ret_sucess("注册成功")


def gen_user_no():
    """
    生成user_no
    :return: user_no
    """

    # 生成随机数
    user_no_random = random.randint(1, 9)
    # 生成uuid
    user_no_uuid = uuid.uuid1().int
    # 获取当前时间
    user_no_time = datetime.datetime.now().strftime("%f")
    # 拼接随机数、时间与uuid的后2位
    user_no = str(user_no_random) + user_no_time + str(user_no_uuid)[-2:]

    return int(user_no)


def gen_user_pwd(user_pwd):
    """
    生成user_pwd的md5值
    :param user_pwd: 用户输入的密码
    :return: user_pwd的md5值
    """

    return hashlib.md5(user_pwd.encode('utf-8')).hexdigest()
