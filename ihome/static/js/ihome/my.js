function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// TODO: 点击推出按钮时执行的函数
function logout() {
    $.ajax({
        url:'/api/1.0/sessions',
        type: 'delete',
        headers:{'X-CSRFToken':getCookie('csrf_token')},
        success: function (data) {
                if('0' == data.errno){
                    location.href = '/';
                }else {
                    alert(data.errmsg);
                }
            }
    })
}

$(document).ready(function(){

    // TODO: 在页面加载完毕之后去加载个人信息
    $.get('/api/1.0/users',function (data) {
        if('0' == data.errno){
            $('#user-name').html(data.user_dict.name);
            $('#user-mobile').html(data.user_dict.mobile);
            $('#user-avatar').attr('src',data.user_dict.avatar_url);

        }else if ('4101' == data.errno) {
            location.href = 'login'
        }else {
            alert('请完善个人信息')
        }
    })

});
