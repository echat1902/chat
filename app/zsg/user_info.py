"""
本模块包括：
个人信息展示
个人信息修改
"""
import datetime
import os

from flask import redirect, render_template, request, jsonify

from app import db
from app.common.funs import chkLogin, ret_sucess, ret_error
from app.models import User
from app.zsg.form_check import FormCheck
from . import zsg


@zsg.route("/user_info", methods=['GET', 'POST'])
def user_info():
    """
    用户个人信息视图函数
    :return: get 用户个人信息界面
             post 修改成功
    """

    # 检查用户是否处于登录状态，如果不是，跳转到登录界面
    user_no = chkLogin()
    if not user_no:
        return redirect('/login')

    user = User.query.filter_by(user_no=user_no).first()
    if request.method == 'GET':
        # 返回用户个人信息
        return render_template("index.html", user=user)
    else:
        # 修改用户个人信息
        user.user_nick_name = request.form['user_nick_name']
        user.user_tel = request.form['user_tel']
        user.user_email = request.form['user_email']
        # 检查用户信息
        res = info_check(user.user_nick_name, user.user_tel, user.user_email)
        if res != True:
            return ret_error(res)

        # 保存用户信息
        db.session.add(user)

        return ret_sucess("修改成功")


@zsg.route('/user_head_upload', methods=['POST'])
def user_head_upload():
    """
    头像上传视图函数
    :return: 成功code:1/失败code:0
    """

    # 检查用户是否登录
    user_no = chkLogin()
    if not user_no:
        return redirect('/login')

    user = User.query.filter_by(user_no=user_no).first()

    if 'file' in request.files:
        # 获取上传的头像
        pic = request.files['file']
        pic_name = gen_pic_name(pic)
        if pic_name == '':
            # 如果生成文件名为空，则该文件不是图片
            return jsonify({'code': 0, 'msg': '请选择一张图片'})

        pic_path = gen_pic_path(pic_name)
        # 保存图片
        pic.save(pic_path)
        # 修改用户头像图片目录及图片名
        user.user_head_pic = pic_path
        user.pic_name = pic_name
        db.session.add(user)

    return jsonify({'code': 1, 'msg': '上传成功'})


def info_check(name, tel, email):
    """
    检查用户信息
    :param name: 用户名
    :param tel: 手机号
    :param email: 邮箱
    :return: 错误信息/True
    """

    # 检查用户名
    res = FormCheck.name_check(name)
    if res == True:
        # 检查电话号
        res = FormCheck.tel_check(tel)
        if res == True:
            # 检查邮箱
            res = FormCheck.email_check(email)
    return res


def gen_pic_name(pic):
    """
    生成头像图片名
    :param pic: 用户上传的头像图片
    :return: 返回'' 代表用户上传的头像不是.jpg或.png格式
             或者返回生成的头像图片名pic_name
    """

    # 获取扩展名
    ext = pic.filename.split('.')[-1]
    # 头像文件校验
    res = FormCheck.pic_check(ext)
    if not res:
        # 用户上传的文件不是图片格式，返回空字符串
        return ''

    ftime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    pic_name = ftime + '.' + ext
    return pic_name


def gen_pic_path(pic_name):
    """
    生成头像图片路径
    :param pic_name: 头像图片名
    :return: 头像图片路径
    """

    this_dir = os.path.dirname(__file__)
    base_dir = os.path.dirname(this_dir)
    pic_path = os.path.join(base_dir, 'static\images\head', pic_name)
    return pic_path
