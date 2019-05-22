from sqlalchemy import func
from app.common.funs import *
from app.common.funs import get_date
from app.models import *
from ..models import ChatList, ChatRecords


def server_recv_model(msg_dict):
    """服务端接收的数据格式"""
    # msg_dict = {'lid': lid,
    #            'user_nick_name': user_nick_name,
    #            'pic_name': pic_name,
    #            'send_msg': msg.html()}


def build_record_msg(message,send_id,group_id,content_type,int_time,recv_id=None):
    return {
        "lid": message["lid"],
        "send_user_id": send_id,
        "group_id": group_id,
        "recv_user_id": str(recv_id),
        "content": message["send_msg"].encode(),
        "content_type": content_type,
        "add_time": int_time
    }



def client_recv_model(user_no,nick_name,content,content_type,int_time,group_id=0,recv_user_no=[]):
    """
    服务端发送的数据格式
    :param user_no:
    :param nick_name:
    :param content:
    :param content_type:
    :param int_time:
    :param group_id:
    :param recv_user_no:
    :return:
    """
    msg_dict = {
        "send_user_no":user_no,#发送者易号
        "send_user_nick_name":nick_name,#发送者群昵称/私聊则本名
        "content":content,#消息内容
        "content_type": content_type, # int消息格式消息格式1文本/2文件
        "send_time":get_date(int_time),
        "group_id":group_id,#0私聊/群id
        "recv_no": recv_user_no,  # 群聊＠用户名，默认为[]
    }
    return msg_dict


def get_lastleave_record_obj(user_id):
    """
    获取记录表里该用户上次离开后所有用户的聊天记录
    :param user_no:
    :return:
    """

    lastleave_recordid = db.session.query(func.max(ChatRecords.record_id)).filter(ChatRecords.send_user_id==user_id,ChatRecords.content_type==5).first()[0]
    return db.session.query(ChatRecords).filter(ChatRecords.record_id>lastleave_recordid).all()


def get_obj_by_lid(lid):
    """
    根据lid获取该对象
    :param lid:
    :return:
    """
    return db.session.query(ChatList).filter(ChatList.lid==lid).first()


def update_chatlist_one(obj,pri_id,sub_id,content,add_time):
    obj.pri_user_id = pri_id
    obj.sub_user_id = sub_id
    obj.content = content
    obj.update_time = add_time
    db.session.add(obj)


def update_chatlist_group(obj,pri_id,content,add_time):
    obj.pri_user_id = pri_id
    obj.content = content
    obj.update_time = add_time
    db.session.add(obj)


def get_after_leave_msg(user_no):
    user_id = query_user_id(user_no)
    user_groups = get_group_list(user_id)
    record_objs = get_lastleave_record_obj(user_id)
    msgs_list = []
    for x in record_objs:
        if x.group_id in user_groups:
            send_user_no = query_user_no(x.send_user_id)
            send_nick_name = query_user_groupnick_name(x.send_user_id,x.group_id)
            special_no_list = get_special_no_by_recordstr(x.recv_user_id)
            msg = client_recv_model(send_user_no,send_nick_name,x.content,x.content_type,x.add_time,x.group_id,special_no_list)
            msgs_list.append(msg)
        elif x.group_id == 0 and int(x.recv_user_id) == user_id:
            send_user_no = query_user_no(x.send_user_id)
            send_user_name = query_user_self_nink_name(x.send_user_id)
            msg = client_recv_model(send_user_no,send_user_name,x.content,x.content_type,x.add_time,x.group_id)
            msgs_list.append(msg)
        else:
            continue
    return msgs_list

def get_group_list(user_id):
    return db.session.query(GroupUser.group_id).filter(GroupUser.user_id==user_id).all()


def get_id_by_nickname(nickname):
    return db.session.query(User.user_id).filter(User.user_nick_name==nickname).first()[0]

def get_recv_id_one(obj,id):
    if obj.pri_user_id == id:
        return obj.sub_user_id
    else:
        return obj.pri_user_id


def get_recv_id_group(obj,id):
    if obj.pri_user_id == id:
        return obj.group_id


def get_special_str(recv_userno_list):
    """
    将＠的用户易号列表转换为id字符串
    :param recv_userno_list:
    :return:
    """
    user_id_list = []
    if not recv_userno_list:
        return ''
    for x in recv_userno_list:
        user_id_list.append(query_user_id(x))
    str_id = ""
    for x in range(len(user_id_list)):
        if x == len(user_id_list):
            str_id += str(user_id_list[x])
        else:
            str_id += str(user_id_list[x]) + ","
    return str_id

def get_grouplist_recv_userno(list_user_id):
    """
    根据用户id列表获得用户易号列表
    :param list_user_id:
    :return:
    """
    return [query_user_no(x) for x in list_user_id]


def get_special_no_by_recordstr(str):
    if not str:
        return []
    str_id_list = str.split(",")
    return [query_user_no(int(x)) for x in str_id_list]

def save_into_record(lid,msg_dict,send_user_id,recv_special,int_time):
    """
    将消息记录存入数据库的消息记录表
    :param lid:
    :param msg_dict:
    :param send_user_id:
    :param recv_special:
    :param int_time:
    :return:
    """
    record_dict={
        "lid":lid,
        "send_user_id":send_user_id,
        "group_id":msg_dict["group_id"],
        "recv_user_id":recv_special,
        "content":msg_dict["content"],
        "content_type":msg_dict["content_type"],
        "add_time":int_time
    }
    ChatRecords.add_one(**record_dict)

def save_into_chat_list(pri_id,sub_id,group_id,type,content,update_time):
    """
    将最后一条消息存入chatlist中
    :param pri_id:
    :param sub_id:
    :param group_id:
    :param type:
    :param content:
    :param update_time:
    :return:
    """
    the_dict = {
        "pri_user_id":pri_id,
        "sub_user_id":sub_id,
        "group_id":group_id,
        "type":type,
        "content":content,
        # "list_sort":list_sort,
        "update_time":update_time
    }
    if db.session.query(ChatList.lid).filter(ChatList.pri_user_id==pri_id,ChatList.sub_user_id==sub_id,ChatList.group_id==group_id).first()[0]:
        ChatList.update(**the_dict)
    else:
        ChatList.add_one(**the_dict)

def get_lid_by_chatlist(pri_id,sub_id=None,group_id=None):
    """
    获取lid
    :param pri_id:
    :param sub_id:
    :param group_id:
    :return:
    """
    if sub_id:
        return db.session.query(ChatList.lid).filter(ChatList.pri_user_id==pri_id,ChatList.sub_user_id==sub_id).first()[0]
    else:
        return db.session.query(ChatList.lid).filter(ChatList.pri_user_id==pri_id,ChatList.group_id==group_id).first()[0]

def get_special_id(list_special_no):
    """
    根据＠user_no列表获取user_id列表
    :param list_special_no:
    :return:
    """
    if list_special_no:
        return [query_user_id(x) for x in list_special_no]


def query_one_uname(send_id,recv_id):
    """
    通过发送者及接收者id查询判断是否好友
    :param send_id:
    :param recv_id:
    :return: Bool
    """
    if db.session.query(Relation).filter(Relation.pri_id==send_id,Relation.sub_id==recv_id,Relation.relation_type==1).first()[0]:
        return True
    return False


def query_user_self_nink_name(the_user_id):
    """
    根据用户id查询自己的昵称
    :param the_user_id:
    :return:
    """
    return db.session.query(User.user_nick_name).filter(User.user_id==the_user_id).first()[0]


def query_user_groupnick_name(the_user_id,group_id):
    """
    根据用户id查询群昵称
    :param the_user_id:
    :return:
    """
    return db.session.query(GroupUser.user_nick_name).filter(GroupUser.user_id==the_user_id,GroupUser.group_id==group_id).first()[0]

def query_group_userid(the_group_id):
    """
    根据群id查询该群用户id列表
    :param the_group_id:
    :return:
    """
    return db.session.query(GroupUser.user_id).filter(GroupUser.group_id==the_group_id).all()

def query_user_no(the_user_id):
    """
    根据用户id查询易号
    :param the_user_id:
    :return:
    """
    return db.session.query(User.user_no).filter(User.user_id==the_user_id).first()[0]

def query_user_id(the_user_no):
    """
    根据易号查id
    :param the_user_no:
    :return:
    """
    return db.session.query(User.user_id).filter(User.user_no == the_user_no).first()[0]