/*
    layui js主入口
*/
layui.define(['upload', 'layer', 'form'], function (exports) {
    var upload = layui.upload;
    var layer = layui.layer;
    var form = layui.form;

    // 头像上传
    upload.render({
        elem: '#user_head_upload'
        ,url: '/user_head_upload'
        // 选择文件后的回调函数
        ,choose: function (obj) {
            // 预读本地文件, index为文件索引, file为文件对象, result为文件base64编码
            obj.preview(function (index, file, result) {
                var reader =new FileReader();
                reader.onload = function (event) {
                    // 更改用户个人信息页与聊天界面的个人头像
                    $('#user_info_show .user_head_show img').attr('src', result);
                    $('.own_head').css('background', 'url('+result+')').css('background-size', 'contain');
                };
                reader.readAsDataURL(file);
            })
        }
        // 执行上传请求成功后的回调函数
        ,done: function (res) {
            layer.msg(res.msg, {time: 1000});
        }
    });

    // 个人信息表单提交
    form.on('submit(user_info_form)', function () {
        // 向后端发送post请求
        $.post('/user_info', $('#user_info_show form').serialize(), function (res) {
            layer.msg(res.msg, {time: 1000}, function () {
                if(res.code == 1){
                    layer.close(index2)
                }
            });
        }, 'json');

        return false;
    });

    exports('layui_index', {});
});
