function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function hrefBack() {
    history.go(-2);
}


function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}


$(document).ready(function() {
    var queryData = decodeQuery();
    var next = queryData["next"];
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    // 添加登录表单提交操作
    $(".form-login").submit(function(e){
        e.preventDefault();
        var mobile = $("#mobile").val();
        var passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        var params = {
            'mobile':mobile,
            'password':passwd
        };
        $.ajax({
            url : '/api/1.0/sessions',
            type : 'post',
            data :  JSON.stringify(params),
            contentType: "application/json",
            headers : {
                'X_CSRFToken':getCookie('csrf_token')
            },
            dataType : 'json',
            success: function (data) {
                if('0' == data.errno){
                    // if(next){
                    //     // hrefBack();
                    //     history.back();
                    //     return;
                    // }
                    location.href = '/';

                }else {
                    alert(data.errmsg);
                }
            }


        })
    })
});
