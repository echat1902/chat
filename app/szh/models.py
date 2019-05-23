from sqlalchemy import func
from app.common.funs import *

from app.models import *
from ..models import ChatList, ChatRecords,YlFiles


def server_recv_model():
    """服务端接收的数据格式"""
    # msg_dict = {'lid': lid,
    #            'send_user_id': user_id,
    #            'msg_type':str
    #            'send_msg': msg.html()}

    # msg_dict = lid,\
    #            file_path,\
    #            file_name,\
    #            msg_type,\
    #            file_size,\
    #            send_user_id,\
    #            recv_user_id=None


def build_record_msg(message,send_id,obj,int_time,content,recv_id=None):
    """
    将要储存进消息记录的数据转化为字典
    :param message:
    :param send_id:
    :param obj:
    :param int_time:
    :param content:
    :param recv_id:
    :return:
    """
    content_type = int(message["msg_type"])
    lid = int(message["lid"])
    if recv_id:#群聊天＠人时
        return {
            "lid": lid,
            "send_user_id": send_id,
            "group_id": obj.group_id,
            "recv_user_id": str(recv_id),
            "content": content.encode(),
            "content_type": content_type,
            "add_time": int_time
        }
    else:
        if obj.type == 1:#
            recv_id = get_recv_id_one(obj,send_id)#获取接收消息的用户id
            return {
                "lid": lid,
                "send_user_id": send_id,
                "group_id": obj.group_id,
                "recv_user_id": str(recv_id),
                "content": content.encode(),
                "content_type": content_type,
                "add_time": int_time
            }
        #普通群聊
        return {
            "lid": lid,
            "send_user_id": send_id,
            "group_id": obj.group_id,
            "content": content.encode(),
            "content_type": content_type,
            "add_time": int_time
        }


def add_file_yi_file(message,int_time,group_id=None,recv_id=None):
    """
    将文件信息添加到文件表
    :param obj:
    :param content:
    :param int_time:
    :return:
    """
    if not group_id:#私聊文件
        file_dict = {
            "send_user_id":int(message["send_user_id"]),
            "recv_user_id":recv_id,
            "file_name":message["file_name"],
            "file_path":message["file_path"],
            "file_size":message["file_size"],
            "add_time":int_time
        }
    else:#群聊文件
        file_dict = {
            "send_user_id": int(message["send_user_id"]),
            "group_id": group_id,
            "file_name": message["file_name"],
            "file_path": message["file_path"],
            "file_size": message["file_size"],
            "add_time": int_time
        }
    YlFiles.add_one(**file_dict)


def get_file_id(pri_id,int_time):
    """
    根据发送者跟时间获取文件id
    :param pri_id:
    :param int_time:
    :return:
    """
    return db.session.query(YlFiles.file_id).filter(YlFiles.send_user_id==pri_id,YlFiles.add_time==int_time).first()[0]


def get_pick_name(obj,send_id):
    """
    根据lid对象及用户id返回个人昵称或群昵称
    :param lid:
    :param send_id:
    :return:
    """
    if obj.group_id == 0:
        return query_user_pic_name(send_id)
    return query_user_groupnick_name(send_id,obj.group_id)


def get_obj_by_lid(lid):
    """
    根据lid获取该对象
    :param lid:
    :return:
    """
    return db.session.query(ChatList).filter(ChatList.lid==lid).first()


def update_chatlist(obj,pri_id,content,add_time):
    """
    更新chatlist中的最后一条信息（包括私聊群聊）
    :param obj:
    :param pri_id:
    :param content:
    :param add_time:
    :param sub_id:
    :param group_id:
    :return:
    """
    if obj.type ==1:
        if obj.pri_user_id != pri_id:
            obj.sub_user_id = obj.pri_user_id
    obj.pri_user_id = pri_id
    obj.content = content
    obj.update_time = add_time
    db.session.add(obj)


def update_chatlist_group(obj,pri_id,content,add_time):
    """
    更新chatlist的群最后一条信息
    :param obj:
    :param pri_id:
    :param content:
    :param add_time:
    :return:
    """
    obj.pri_user_id = pri_id
    obj.content = content
    obj.update_time = add_time
    db.session.add(obj)


def get_id_by_nickname(nickname):
    """
    根据nickname获取用户id
    :param nickname:
    :return:
    """
    return db.session.query(User.user_id).filter(User.user_nick_name==nickname).first()[0]


def get_recv_id_one(obj,id):
    """
    chatlist的查询对象和发送id获取私聊的接收id或群id
    :param obj:
    :param id:
    :return:
    """
    if obj.type == 2:
        return obj.group_id
    if obj.pri_user_id == id:
        return obj.sub_user_id
    else:
        return obj.pri_user_id


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


def query_user_pic_name(send_user_id):
    return db.session.query(User.pic_name).filter(User.user_id==send_user_id).first()[0]


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