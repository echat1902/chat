"""
视图函数中调用的函数
"""
import datetime
import os

from app.zsg.form_check import FormCheck


def info_check(name, tel, email, user):
    """
    检查表单数据
    :param name: 用户名
    :param tel: 手机号
    :param email: 邮箱
    :param user: 用户实体
    :return: 错误信息/True
    """

    res = True
    # 检查用户名
    if user.user_nick_name != name:
        res = FormCheck.name_check(name)
    # 检查电话号
    if res == True and user.user_tel != tel and tel != '':
        res = FormCheck.tel_check(tel)
    # 检查邮箱
    if res == True and user.user_email != email and email != '':
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
    pic_path = os.path.join(base_dir, 'static/images/head', pic_name)
    return pic_path
