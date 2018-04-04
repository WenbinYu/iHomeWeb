function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// TODO: 点击推出按钮时执行的函数
function logout() {
    $.ajax({
        url:'/api/1.0/sessions',
        type: 'delete',
        headers : {
            'X_CSRFToken': getCookie('crsf_token')
        },
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

});
