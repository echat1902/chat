# 管理和启动项目
from app import create_app

from flask_socketio import SocketIO,join_room,leave_room
import json
from app.szh.models import *

app = create_app()
socketio = SocketIO(app)


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
                    "file_name": message["file_name"], "file_ext": ext, "filesize": message["file_size"],"file_path":message["file_path"]}
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
    lid = str(data['lid'])
    join_room(lid)



@socketio.on('disconnect', namespace='/chat')
def test_disconnect(data):
    lid = str(data['lid'])
    leave_room(lid)



if __name__ == '__main__':
    socketio.run(app, debug=True)