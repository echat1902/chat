import operator

from app.common.funs import chkLogin
from . import tg
from flask import render_template, request, session, redirect, make_response, abort
from .models import *
from app.common.funs import *
from app.models import *
from manager1 import socketio
from flask_socketio import emit,join_room,leave_room
from app.szh.models import *

# from manager import socketio

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
        res = db.session.query(ChatList.lid, ChatList.update_time,Ylgroup.group_id, Ylgroup.group_no, Ylgroup.group_name,
                               Ylgroup.pic_name).join(GroupUser,
                                                      ChatList.group_id == GroupUser.group_id).filter(
            GroupUser.user_id == user_id).join(
            Ylgroup, GroupUser.group_id == Ylgroup.group_id).all()
        for i in res:
            group_info = {}
            group_info['lid'] = i[0]
            group_info['update_time'] = get_date(i[1])
            group_info['group_id'] = i[2]
            group_info['group_no'] = i[3]
            group_info['group_name'] = i[4]
            group_info['pic_name'] = i[5]
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



@socketio.on('imessage', namespace='/flasksocketio')
def test_message(message):
    msg_type = int(message["msg_type"])
    send_user_id = int(message["send_user_id"])
    lid = int(message["lid"])
    obj = get_obj_by_lid(lid)
    user_nick_name = get_nick_name(obj, send_user_id)  # 根据lid查询对象返回个人昵称或群昵称
    pic_name = query_user_pic_name(send_user_id)
    recv_id = get_recv_id_one(obj, send_user_id)  # 接收id或群id
    int_time = get_time()
    if msg_type == 3:  # 文件
        ext = message["file_name"].split(".")[-1]  # 获取文件后缀名
        chatlist_content = "[文件]"
        if obj.type == 1:  # 私聊
            add_file_yi_file(message, int_time, recv_id=recv_id)
        else:  # 群聊
            add_file_yi_file(message, int_time, group_id=recv_id)
        content = str(get_file_id(send_user_id, int_time))  # 消息记录内容为文件记录表中该文件的id
        msg_dict = {"lid": lid, "user_nick_name": user_nick_name, "pic_name": pic_name, "msg_type": msg_type,
                    "file_name": message["file_name"], "file_ext": ext, "filesize": message["file_size"]}
    elif msg_type == 2:  # 图片
        chatlist_content = "[图片]"
        content = message["send_msg"]
        msg_dict = {"lid": lid, "user_nick_name": user_nick_name, "pic_name": pic_name, "send_msg": message["send_msg"],
                    "msg_type": msg_type}
    elif msg_type == 1:  # 文本
        chatlist_content = message["send_msg"]
        content = message["send_msg"]
        msg_dict = {"lid": lid, "user_nick_name": user_nick_name, "pic_name": pic_name, "send_msg": message["send_msg"],
                    "msg_type": msg_type}

    record_dict = build_record_msg(message, send_user_id, obj, int_time, content)  # 组织成消息记录格式
    ChatRecords.add_one(**record_dict)  # 将消息记录存入消息记录表
    update_chatlist(obj, send_user_id, chatlist_content, int_time)  # 更新chatlist的该房间最后一条消息
    socketio.emit('server_response', json.dumps(msg_dict), room=str(message['lid']), namespace='/flasksocketio')


@socketio.on('join room', namespace='/flasksocketio')
def test_connect(data):
    lid = data['lid']
    join_room(lid)



@socketio.on('disconnect', namespace='/chat')
def test_disconnect(data):
    lid = data['lid']
    leave_room(lid)




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
