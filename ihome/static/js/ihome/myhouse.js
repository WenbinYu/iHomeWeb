$(document).ready(function(){
    //  对于发布房源，只有认证后的用户才可以，所以先判断用户的实名认证状态
     $.get('/api/1.0/users/auth',function (data) {
        if('0' == data.errno){
              if (data.resp.auth_dict.real_name && data.resp.auth_dict.id_card){
                  $('.auth-warn').hide();
                  $('#houses-list').show();
                  var html = template('houses-list-tmpl',{houses:data.resp.houses});
                  $('#houses-list').html(html)
              }else {
                   $('.auth-warn').show();
                    $('#houses-list').hide();
              }

        }else if ('4101' == data.errno) {
            location.href = 'login?next='+data.next_url
        }else {
            alert('请完善个人信息')
        }
    });

});
