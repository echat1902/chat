from flask import render_template,request

from manager import socketio
from .models import *
from . import szh
from app.common.funs import *
from flask_socketio import emit,join_room,leave_room
import json,time

# app目录
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 当前时间戳(毫秒)
mill_time = get_mill_time()
# 上传文件目录
upload_path = chk_path(os.path.join(app_dir, 'static', 'upload'))



# 示例
# 本地测试访问地址 http://localhost:5000/interGroup
@szh.route('/interGroup')
def add_fri():
    return '进入群成功'


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
    lid = data['lid']
    join_room(lid)



@socketio.on('disconnect', namespace='/chat')
def test_disconnect(data):
    lid = data['lid']
    leave_room(lid)
#
#
#
#




# 文件上传
@szh.route('/file/upload/<now_time>', methods=['POST'])
def upload_part(now_time):  # 接收前端上传的一个分片
    task = request.form.get('task_id')  # 获取文件的唯一标识符
    chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
    filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符
    upload_file = request.files['file']
    path = chk_path(os.path.join(upload_path, str(now_time)))
    file_name = os.path.join(path, filename)
    upload_file.save(file_name)  # 保存分片到本地
    return json.dumps({})


@szh.route('/file/merge', methods=['GET'])
def upload_success():  # 按序读出分片内容，并写入新文件
    target_filename = request.args.get('filename')  # 获取上传文件的文件名
    task = request.args.get('task_id')  # 获取文件的唯一标识符
    now_time = request.args.get('now_time')
    path = chk_path(os.path.join(upload_path, str(now_time)))
    upload_file = os.path.join(path, target_filename)

    chunk = 0  # 分片序号
    with open(upload_file, 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = os.path.join(upload_path, str(now_time), task + str(chunk))
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())  # 读取分片内容写入新文件
                source_file.close()
            except IOError as msg:
                break

            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间

    return json.dumps({})