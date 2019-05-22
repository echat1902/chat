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


# 添加好友
@hhb.route('/addFriend', methods=['GET', 'POST'])
def add_friend():
    if request.method == 'GET':
        # 接收前端传递过来的用户昵称
        user_no = request.args['user_no']
        # 根据用户昵称查询对应的用户
        user = User.query.filter_by(user_no=user_no).first()
        return render_template('addfriend.html', user=user)
    else:
        # 接收前端传过来的数据

        pri_id = request.form['pri_id']
        sub_id = request.form['sub_id']
        # remark = request.form['remark']
        # 状态为陌生人
        relation_tipe = 3
        # 查询relation数据库中是否存在该关系
        re = db.session.query(Relation).filter_by(pri_id=pri_id, sub_id=sub_id).first()
        if re:
            return "已经是好友，不能重复添加"
        else:
            # 创建friend对象并且为属性赋值
            friend = Relation()
            friend.pri_id = pri_id
            friend.sub_id = sub_id
            # friend.remark = remark
            friend.relation_type = relation_tipe
            friend.add_time = get_time()
            # 将friend保存进数据库
            db.session.add(friend)

            return '添加好友成功'


# 同意好友请求或拒绝
@hhb.route('/friRequest', methods=['GET', 'POST'])
def fri_request():
    # 用户收到好友申请提示，点击查看，发起get请求
    if request.method == 'GET':
        # 接收前端传过来的数据
        user_no = request.args['user_no']
        user = User.query.filter_by(user_no=user_no).first()
        return render_template('fri_request.html', user=user)
    else:
        # 接收前端传过来的数据
        pri_id = request.form['pri_id']
        sub_id = request.form['sub_id']
        relation_type = request.form['relation_type']
        # 同意则修改状态并更新回数据库
        if 'relation_type' in request.form:
            relation_type = 1
        friend = Relation.query.filter_by(pri_id=pri_id, sub_id=sub_id).first()
        friend.sub_id = sub_id
        friend.pri_id = pri_id
        friend.relation_type = relation_type
        friend.add_time = get_time()
        db.session.add(friend)
        return "添加好友成功"


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
