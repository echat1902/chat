"""
表单校验模块
"""
import re

from app.models import User


class FormCheck():
    """
    表单校验类
    """

    @staticmethod
    def name_check(user_name):
        """
        用户名校验
        校验规则：用户名不能为空
                 用户名长度应该小于128位
        :param user_name: 用户名
        :return: 错误信息/True
        """

        if user_name == '':
            return "用户名不能为空"
        elif len(user_name) >= 128:
            return "用户名长度应该小于128位"
        else:
            user = User.query.filter_by(user_nick_name=user_name).first()
            if user:
                return "该用户名已存在"
        return True

    @staticmethod
    def pwd_check(user_pwd):
        """
        密码校验
        校验规则：密码不能为空
                 密码长度应该小于40位
        :param user_pwd: 密码
        :return: 错误信息/True
        """

        if user_pwd == '':
            return "密码不能为空"
        elif len(user_pwd) >= 40:
            return "密码长度应该小于40位"
        return True

    @staticmethod
    def tel_check(user_tel):
        """
        电话号校验
        校验规则：regex
        :param user_tel: 电话号
        :return: 错误信息/True
        """

        res = re.fullmatch(r'1[0-9]{10}', user_tel)
        if not res:
            return "请输入正确的手机号"
        return True

    @staticmethod
    def email_check(user_email):
        """
        邮箱校验
        校验规则：regex
        :param user_email: 邮箱
        :return: 错误信息/True
        """

        res = re.fullmatch(r'\w+@\w+.\w+', user_email)
        if not res:
            return "请输入正确的邮箱"
        return True

    @staticmethod
    def pic_check(ext):
        """
        头像文件校验
        校验规则：用户上传的头像必须是.jpg或.png格式
        :param ext: 头像文件扩展名
        :return: False/True
        """

        if ext not in ['jpg', 'png']:
            return False
        return True
