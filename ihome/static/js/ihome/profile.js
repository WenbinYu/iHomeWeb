function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // TODO: 在页面加载完毕向后端查询用户的信息
     $.get('/api/1.0/users',function (data) {
        if('0' == data.errno){
            $('#user-name').val(data.user_dict.name);
            $('#user-avatar').attr('src',data.user_dict.avatar_url);

        }else if ('4101' == data.errno) {
            location.href = 'login'
        }else {
            alert('请完善个人信息')
        }
    });

    // TODO: 管理上传用户头像表单的行为
    $('#form-avatar').submit(function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            url:'/api/1.0/users/avatar',
            type:'post',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function(response) {
                if (response.errno == '0') {
                    // 上传头像成功，刷新出头像
                    showSuccessMsg()
                    $('#user-avatar').attr('src', response.avatar_uravl);

                } else if ('4101' == response.errno ) {
                    location.href = 'login';
                } else {
                    alert(response.errmsg);
                }
            }
        });
    });
    // TODO: 管理用户名修改的逻辑
     $('#form-name').submit(function (e) {
        e.preventDefault();
        var new_name = $('#user-name').val();
         if (!new_name){
            alert('请确认修改用户名');
            return;
         }
         var params = {
                'new_name': new_name
            };
        $.ajax({
            url:'/api/1.0/users/name',
            type:'put',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function(response) {
                if (response.errno == '0') {
                    // 上传头像成功，刷新出头像
                    showSuccessMsg();

                } else if ('4101' == response.errno ) {
                    location.href = 'login';
                } else {
                    alert(response.errmsg);
                }
            }
        });
    });

});

