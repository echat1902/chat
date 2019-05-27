from _operator import or_

from sqlalchemy import delete

from . import hhb
from flask import render_template
from app.common.funs import *
from app.models import *


# 示例
# 本地测试访问地址 http://localhost:5000/addFri
# 点击加好友按钮，返回一个搜索框
@hhb.route('/search')
def search():
    return render_template('search.html')


# 获取用户/群信息
@hhb.route('/getUserInfo')
def get_user_info():
    value = int(request.args['value'])
    # 根据用户昵称或易号查询对应的用户

    data = User.query.filter(or_(User.user_no == value, User.user_nick_name == value)).first()
    if data:
        data = data.to_json()
    else:
        data = Ylgroup.query.filter_by(group_no=value).first()
        if data:
            data = data.to_json()
        else:
            return ret_error('用户或群不存在')
    return ret_sucess('获取成功', data)


# 申请添加好友
@hhb.route('/addFriend', methods=['GET', 'POST'])
def add_friend():
    # 接收前端传过来的数据
    pri_id = request.form['pri_id']
    sub_id = request.form['sub_id']
    obj_type = int(request.form['obj_type'])
    # 获取用户信息
    uinfo = User.query.filter_by(user_id=pri_id).first()
    words = '你好,我是' + uinfo.user_nick_name
    remark = request.form.get('remark', words)
    # 如果是加好友
    if obj_type == 1:
        # 不能添加自己
        if pri_id == sub_id:
            return ret_error('不能添加自己')
        # 查询relation数据库中是否存在该关系
        re = db.session.query(Relation).filter_by(pri_id=pri_id, sub_id=sub_id).first()
        if re:
            return ret_error("已经是好友或已经申请")
        else:
            # 状态为陌生人
            relation_type = 3
            # 第一步：Relation表中添加一条数据
            user_info = {'pri_id': pri_id, 'sub_id': sub_id, 'remark': remark, 'relation_type': relation_type,
                         'add_time': get_time()}
            Relation.add_one(**user_info)
            return ret_sucess('申请成功')
    else:
        # 加群
        words = '大家好,我是' + uinfo.user_nick_name
        # 根据group_no获取group信息
        gi = Ylgroup.query.filter_by(group_no=sub_id).first()
        group_id = gi.group_id
        # 查询group_user数据库中是否存在该关系
        re = db.session.query(GroupUser).filter_by(user_id=pri_id, group_id=group_id).first()
        if re:
            return ret_error("已经加入了该群，不能重复添加")
        else:
            # 第一步：group_user表中添加一条数据
            group_info = {'user_id': pri_id, 'group_id': group_id, 'user_nick_name': uinfo.user_nick_name,
                          'user_pic': uinfo.pic_name,
                          'add_time': get_time()}
            GroupUser.add_one(**group_info)
            # 第二步：查出该群的lid
            lid_info = ChatList.query.filter(ChatList.group_id == group_id).first()
            if not lid_info:
                # 插入chat_list
                add_data = {'group_id':group_id,'type':2,'content':words,'update_time':get_time()}
                ChatList.add_one(**add_data)
            lid_info = ChatList.query.filter(ChatList.group_id == group_id).first().to_json()
            lid_info['group_name'] = gi.group_name
            lid_info['pic_name'] = gi.pic_name
            lid_info['update_time'] = get_date(lid_info['update_time'])

            #第三步：群成员+1
            gi.num = gi.num + 1
            db.session.add(gi)

        return ret_sucess('添加成功',lid_info)


# 同意好友请求
@hhb.route('/friRequest', methods=['GET', 'POST'])
def fri_request():
    # 用户收到好友申请提示，点击查看，发起get请求
    if request.method == 'GET':
        # 接收前端传过来的数据
        user_id = request.args['user_id']
        # 查询该用户的好友申请列表
        res = db.session.query(Relation.pri_id, Relation.remark, Relation.relation_type, Relation.add_time,
                               User.user_nick_name, User.user_head_pic, User.pic_name).filter(
            Relation.sub_id == user_id, Relation.relation_type == 3).join(User, Relation.pri_id == User.user_id).all()
        data = []
        for i in res:
            uinfo = {}
            uinfo['pri_id'] = i[0]
            uinfo['remark'] = i[1]
            uinfo['relation_type'] = i[2]
            uinfo['add_time'] = i[3]
            uinfo['user_nick_name'] = i[4]
            uinfo['user_head_pic'] = i[5]
            uinfo['pic_name'] = i[6]
            data.append(uinfo)
        return ret_sucess('获取成功', data)

    else:
        # 接收前端传过来的数据
        pri_id = request.form['pri_id']
        sub_id = request.form['sub_id']
        relation_type = 1
        add_time = get_time()
        # 获取用户信息
        uinfo = User.query.filter_by(user_id=pri_id).first()
        user_nick_name = uinfo.user_nick_name
        update_data = {'relation_type': relation_type, 'add_time': add_time}
        # 同意则修改状态并更新回数据库
        Relation.query.filter_by(pri_id=pri_id, sub_id=sub_id).first().update(**update_data)
        # 第二步：chat_list插入数据
        words = '你好,我是' + user_nick_name
        chat_list_info = {'pri_user_id': pri_id, 'sub_user_id': sub_id, 'content': words, 'update_time': get_time()}
        ChatList.add_one(**chat_list_info)
        # 查出刚插入数据的lid
        lid_info = ChatList.query.filter(ChatList.pri_user_id == pri_id,
                                         ChatList.sub_user_id == sub_id).first().to_json()
        lid_info['user_nick_name'] = uinfo.user_nick_name
        lid_info['pic_name'] = uinfo.pic_name
        lid = lid_info['lid']
        return ret_sucess('你们已经是好友了，快去聊天吧', lid_info)





# 删除好友
@hhb.route('/delFriend', methods=['GET', 'POST'])
def del_friend():
    if request.method == 'GET':
        user_no = request.args['user_no']
        user = User.query.filter_by(user_no=user_no).first()
        return render_template('del_friend.html', user=user)
    else:
        # 接收前端传过来的数据
        pri_id = request.form['pri_id']
        sub_id = request.form['sub_id']
        friend = Relation.query.filter_by(pri_id=pri_id, sub_id=sub_id).first()
        friend.add_time = get_time()
        db.session.delete(friend)
        return '删除好友成功'


# 拉黑
@hhb.route('/setBlack', methods=['GET', 'POST'])
def set_black():
    if request.method == 'GET':
        user_no = request.args['user_no']
        user = User.query.filter_by(user_no=user_no).first()
        return render_template('set_black.html', user=user)
    else:
        pri_id = request.form['pri_id']
        sub_id = request.form['sub_id']
        relation_type = request.form['relation_type']
        if 'relation_type' in request.form:
            relation_type = 2
        friend = Relation.query.filter_by(pri_id=pri_id, sub_id=sub_id).first()
        friend.relation_type = relation_type
        friend.add_time = get_time()
        db.session.add(friend)
        return '拉黑成功'
