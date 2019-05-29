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