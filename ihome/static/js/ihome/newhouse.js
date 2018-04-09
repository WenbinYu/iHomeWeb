function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // 在页面加载完毕之后获取区域信息
    $.get('/api/1.0/areas', function (data) {
        if ('0' == data.errno) {
            var list_html = template('areas-tmpl', {areas: data.areas});
            $('#area-id').html(list_html);
        } else {
            alert(data.errmsg);
        }
    });
    // 处理房屋基本信息提交的表单数据
    var facilitys = [];
    $('#form-house-info').submit(function (e) {
        var params = {};
        e.preventDefault();
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
        });
        $(':checkbox:checked[name=facility]').each(function (i, event) {
            facilitys[i] = event.value;
        });
        params['facility'] = facilitys;
        $.ajax({
            url: '/api/1.0/houses',
            type: 'post',
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            data: JSON.stringify(params),
            contentType: "application/json",
            dataType: "json",
            success: function (data) {
                if ("4101" == data.errno) {
                    location.href = 'login?next='+data.next_url
                }
                else if ('0' == data.errno) {
                    $('#form-house-info').hide();
                    $('#form-house-image').show();
                    $('#house_id').val(data.house_id)
                } else {
                    alert(data.errmsg)
                }
            }

        });
        //  处理图片表单的数据
         $('#form-house-image').submit(function (e) {
             e.preventDefault();

             $(this).ajaxSubmit({
                 url: '/api/1.0/house/images',
                 type: 'post',
                 headers: {'X-CSRFToken': getCookie('csrf_token')},
                 success: function (data) {
                    if ("4101" == data.errno) {
                        location.href = 'login?next='+data.next_url
                    }else if('0'==data.errno){
                        $('.house-image-cons').append('<img src="'+data.image_url+'">');
                        $('#house-image').val()
                    }else {
                        alert(data,errmsg)};
                     }
             });
         })

    });
});