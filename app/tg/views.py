import operator

from . import tg
from flask import render_template,redirect, make_response
from .models import *
from app.szh.models import *


# 首页
@tg.route('/')
@tg.route('/index')
def main_index():
    # 判断用户是否已经登录，并获取用户的易号
    user_no = chkLogin()
    if user_no:
        # 获取用户信息
        userinfo = get_user_info_by_no(user_no)
        user_id = userinfo['user_id']
        # 获取主聊天对象
        # res =db.session.query(ChatList).filter_by(pri_user_id=user_id).all()
        res = ChatList.query.filter(or_(ChatList.pri_user_id == user_id, ChatList.sub_user_id == user_id),
                                    ChatList.group_id == 0).all()
        # 获取主聊天对象的信息
        infos = []
        for i in res:
            if i.sub_user_id == user_id:
                o_user_id = i.pri_user_id
            else:
                o_user_id = i.sub_user_id
            # 查出用户信息
            info = User.query.filter_by(user_id=o_user_id).first()

            if info:
                info.content = i.content
                info.lid = i.lid
                info.update_time = get_date(i.update_time)
                infos.append(info)
        # 查出群信息
        res = db.session.query(ChatList.lid,ChatList.content, ChatList.update_time,Ylgroup.group_id, Ylgroup.group_no, Ylgroup.group_name,
                               Ylgroup.pic_name).join(GroupUser,
                                                      ChatList.group_id == GroupUser.group_id).filter(
            GroupUser.user_id == user_id).join(
            Ylgroup, GroupUser.group_id == Ylgroup.group_id).all()
        for i in res:
            group_info = {}
            group_info['lid'] = i[0]
            group_info['content'] = i[1]
            group_info['update_time'] = get_date(i[2])
            group_info['group_id'] = i[3]
            group_info['group_no'] = i[4]
            group_info['group_name'] = i[5]
            group_info['pic_name'] = i[6]
            infos.append(group_info)
        data = [userinfo, infos]
        return render_template('index.html', data=data)
    return redirect('/login')


# 获取聊天记录
@tg.route('/get_chat_records')
def get_chat_records():
    lid = request.args.get('lid')
    user_id = request.args.get('user_id')

    # 获取聊天对象
    res = ChatList.query.filter_by(lid=lid).first()
    # 获取对方信息
    # subinfo = {}
    # if res.sub_user_id:
    #     subinfo = User.query.filter_by(user_id=res.sub_user_id).first().to_json()

    # 获取聊天记录
    res = ChatRecords.query.filter_by(lid=lid).order_by(db.desc(ChatRecords.add_time)).limit(10).all()
    print(res)
    # res = db.session.query(ChatRecords).join(User, ChatRecords.send_user_id == User.user_id).filter(
    #     ChatRecords.lid == lid).order_by(db.desc(ChatRecords.add_time)).limit(10).all()
    re = []
    for i in res:
        re.append(i.to_json())
    result = sorted(re, key=operator.itemgetter('add_time'))
    # records = {'userinfo': subinfo, 'records': []}
    for i in result:
        uinfo = User.query.filter_by(user_id=i['send_user_id']).first().to_json()
        i['userinfo'] = uinfo
        # 如果该条记录为文件
        if i['content_type'] == 3:
            if isinstance(i['content'], bytes):
                file_id = int(str(i['content'], encoding='utf-8'))
            else:
                file_id = int(i['content'])
            # 获取文件信息
            file_info = YlFiles.query.filter_by(file_id=file_id).first().to_json()
            file_info['file_ext'] = file_info['file_name'].split('.')[-1]
            i['file_info'] = file_info

    # print(records)
    return json.dumps(result)





# 登录
@tg.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # user_no = chkLogin()
        user_no = None
        if user_no:
            return redirect('/index?user_no=' + str(user_no))
        return render_template('login.html')
    else:
        # 从客户端获取用户ip
        str_ip = request.remote_addr
        # 将ip转为int类型
        int_ip = ip2int(str_ip)
        user_name = request.form['user_name']
        user_pwd = request.form['user_pwd']
        reme = request.form.get('chkRememberMe', 0)
        # 查询数据库,判断用户名或密码是否正确
        res = chkUserPwd(user_name, user_pwd)
        if res:
            # 更新用户ip
            User.query.filter_by(user_id=res.user_id).first().update(login_ip=int_ip)
            data = {'user_no': res.user_no, 'user_name': user_name}
            data = ret_sucess('登录成功', data)
            # 将用户信息存入session
            session[str(res.user_no)] = {'user_name': user_name, 'user_pwd': user_pwd}
            # 响应数据
            resp = make_response(data)
            # 将用户易号存入cookie
            resp.set_cookie('user_no', str(res.user_no), 60 * 30)
            # 返回数据
            return resp
        else:
            return ret_error('用户名或密码错误')

# # 添加一个用户
# @tg.route('/add_one')
# def add_one():
#     dict_user = {'user_no': 10006, 'user_nick_name': '小诗', 'user_pwd': 'e10adc3949ba59abbe56e057f20f883e',
#                  'user_tel': 13356}
#     # 第一种写法
#     res = User.add_one(**dict_user)
#     # 第二种写法
#     # res = User.add_one(user_no=10006, user_nick_name='小诗', user_pwd='e10adc3949ba59abbe56e057f20f883e', user_tel=13356)
#     return ret_sucess('添加用户成功')


# # 添加多个用户
# @tg.route('/add_many')
# def add_many():
#     list_user = [
#         {'user_no': 10006, 'user_nick_name': '小诗', 'user_pwd': 'e10adc3949ba59abbe56e057f20f883e',
#          'user_tel': 13356},
#         {'user_no': 10007, 'user_nick_name': '小画', 'user_pwd': 'e10adc3949ba59abbe56e057f20f883e',
#          'user_tel': 13358}
#     ]
#     # 添加多个用户
#     res = User.add_many(list_user)
#     return ret_sucess('添加用户成功')


# # 修改
# @tg.route('/update')
# def update():
#     # 把10006的昵称改为'小画',电话改为14365
#     dict_user = {'user_nick_name': '小画', 'user_tel': 14365}
#     # 第一种写法 拆解字典 也是关键字传参
#     User.query.filter_by(user_no=10006).first().update(**dict_user)
#     # 第二种写法
#     # User.query.filter_by(user_no=10006).first().update(user_nick_name='小画', user_tel=14365)
#     return ret_sucess('修改成功')


# # 删除
# @tg.route('/delete')
# def delete():
#     # 删除易号为10006的
#     User.query.filter_by(user_no=10006).first().delete()
#     return ret_sucess('删除成功')
