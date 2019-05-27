"""
本模块包括：
个人信息修改
"""

from flask import redirect, request, jsonify

from app import db
from app.common.funs import chkLogin
from app.models import User
from app.zsg.sub_funs import gen_pic_name, gen_pic_path, info_check
from . import zsg


@zsg.route("/user_info", methods=['POST'])
def user_info():
    """
    用户个人信息修改视图函数
    :return: 成功code:1/失败code:0
    """

    # 检查用户是否处于登录状态，如果不是，跳转到登录界面
    user_no = chkLogin()
    if not user_no:
        return redirect('/login')

    user = User.query.filter_by(user_no=user_no).first()

    # 获取表单数据
    user_nick_name = request.form['user_nick_name']
    user_tel = request.form['user_tel']
    user_email = request.form['user_email']
    # 表单数据校验
    res = info_check(user_nick_name, user_tel, user_email, user)
    if res != True:
        return jsonify({'code': 0, 'msg': res})

    # 修改用户个人信息
    user.user_nick_name = user_nick_name
    user.user_tel = user_tel
    user.user_email = user_email
    # 保存用户信息
    db.session.add(user)

    return jsonify({'code': 1, 'msg': '保存成功'})


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

    return jsonify({'code': 0, 'msg': '上传失败'})
