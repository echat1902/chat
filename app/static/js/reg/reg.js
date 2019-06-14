$(function(){
	var stuList = getStuList();//设置传送信息：学生的集合
	 
	//聚焦失焦input
	$('input').eq(0).focus(function(){
		if($(this).val().length==0){
            $(this).parent().next("div").text('');
			$(this).parent().next("div").append("<p>支持中文，字母，数字，'-'，'_'的多种组合</p>");
		}
	})
	$('input').eq(1).focus(function(){
		if($(this).val().length==0){
            $(this).parent().next("div").text('');
		    $(this).parent().next("div").append("<p>建议使用字母、数字和符号两种以上的组合，6-20个字符</p>");
		}
	})
	$('input').eq(2).focus(function(){
		if($(this).val().length==0){
            $(this).parent().next("div").text('');
			$(this).parent().next("div").append("<p>请再次输入密码</p>");
		}
	})

	//input各种判断
	//用户名：
	$('input').eq(0).blur(function(){
        $(this).parent().next("div").children('p').text("");
		if($(this).val().length==0){

			$(this).parent().next("div").css("color",'#ccc');
		}
	})
	//密码
	$('input').eq(1).blur(function(){
        $(this).parent().next("div").children('p').text("");
		if($(this).val().length==0){
			$(this).parent().next("div").css("color",'#ccc');
		}
	})
//	确认密码
	$('input').eq(2).blur(function(){
        $(this).parent().next("div").children('p').text("");
		if($(this).val().length==0){

			$(this).parent().next("div").css("color",'#ccc');
		}
	})

// 	验证码
//	 验证码刷新
	/*function code(){
		var str="qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPLKJHGFDSAZXCVBNM";
		var str1=0;
		for(var i=0; i<4;i++){
			str1+=str.charAt(Math.floor(Math.random()*62)) 
		}
		str1=str1.substring(1)
		$("#code").text(str1);
	}
	code();
	$("#code").click(code);	*/

// 手机验证码
/*	$('input').eq(5).blur(function () {
		if($(this).val().length==0){
			$(this).parent().next().next('div').text('验证码不能为空').css('color','#f0f');
		}
    })*/
//协议
	$('#xieyi').change(function () {
        if($("#xieyi")[0].checked){
            document.getElementById('submit_btn').disabled=false;
            $('#submit_btn').css({'background':'#e22','cursor':'pointer'});
        }else{
            document.getElementById('submit_btn').disabled=true;
            $('#submit_btn').css({'background':'#ccc','cursor':'text'});

        }
    })

	
//  建立构造函数，构造学生信息模板
	function Student(name,password,tel,id){
         this.name = name;
         this.password = password;
         this.tel = tel;
         this.id = id;
     }
//	获取之前所有已经注册的用户集合
	function getStuList(){
	    var list = localStorage.getItem('stuList');
	    if(list != null){
	        return JSON.parse(list);
	    }else{
	        return new Array();
	    }
	}

})
