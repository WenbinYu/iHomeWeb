function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function(){
    // 判断用户是否登录
    // var is_login = false;
    $.ajaxSettings.async = false;
    $.get('/api/1.0/users/sessions',function (data) {
        // if('0'==data.errno){
        //     is_login = true;
        // }else {
        //    location.href = 'login'
        // }
        if(!data.resp.user_id && !data.resp.name){
            location.href = 'login'
        }
    });
    $.ajaxSettings.async = true;

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function(){
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg("日期有误，请重新选择!");
        } else {
             var sd = new Date(startDate);
             var ed = new Date(endDate);
             var days = (ed - sd)/(1000*3600*24) ;
             var price = $(".house-text>p>span").html();
             var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共"+ days +"晚)");
        }
    });
    var queryData = decodeQuery();
    var houseId = queryData["hid"];

    //  获取房屋的基本信息
    // if (is_login == true){
        $.get('/api/1.0/house/detail/'+ houseId+'?desc=basic'  ,function (data) {
        if('0' == data.errno){
            $('.house-info>img').attr('src',data.resp.house_dict.img_url);
            $('.house-info h3').html(data.resp.house_dict.title);
            $('.house-info span').html(data.resp.house_dict.price/100);
        }else {
            alert(data.errmsg)
        }
    });
        //  订单提交
        $('.submit-btn').on('click',function () {
            var sd = $('#start-date').val();
            var ed = $('#end-date').val();
             var params = {
                 'house_id':houseId,
                 'ed': ed,
                 'sd':sd
             };
             $.ajax({
                     url:'/api/1.0/orders',
                     type:'post',
                     data:JSON.stringify(params),
                     contentType:'application/json',
                     headers:{'X-CSRFToken':getCookie('csrf_token')},
                     success:function (response) {
                         if (response.errno == '0') {
                             location.href = 'orders'
                         }
                         else {
                             alert(response.errmsg)
                         }
                     }

             });
        });

    // }
});
