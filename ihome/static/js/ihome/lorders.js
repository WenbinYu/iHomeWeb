//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    //  查询房东的订单
    $.get('/api/1.0/orders?role=landlord', function (data) {
        if ('0' == data.errno) {
            var html = template('orders-list-tmpl', {orders: data.resp});
            $('.orders-list').html(html);

            // 查询成功之后需要设置接单和拒单的处理
            $(".order-accept").on("click", function () {
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-accept").attr("order-id", orderId);
            });
            $(".modal-accept").on('click',function () {
                 var orderId = $(this).attr("order-id");
                  $.ajax({
                          url:'/api/1.0/orders/status?action=accept',
                          type:'put',
                          data:JSON.stringify({order_id:orderId}),
                          contentType:'application/json',
                          headers:{'X-CSRFToken':getCookie('csrf_token')},
                          success:function (response) {
                              if (response.errno == '0') {
                                $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("待评价");
                                $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                                $("#accept-modal").modal("hide");
                                 $("#reject-modal").modal("hide");

                              }
                              else { alert('response.errmsg')
                              }
                          }
                  });
            });
            $(".order-reject").on("click", function () {
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-reject").attr("order-id", orderId);
            });
            $(".modal-reject").on('click',function () {
                 var orderId = $(this).attr("order-id");
                 var comment = $('#reject-reason').val();
                 if (!comment) {
                     alert('请输入拒接原因');
                     return;
                 }
                 var params = {
                     'order_id': orderId,
                     'comment': comment
                 };
                 $.ajax({
                     url: '/api/1.0/orders/status?action=reject',
                     type: 'put',
                     data: JSON.stringify(params),
                     contentType: 'application/json',
                     headers: {'X-CSRFToken': getCookie('csrf_token')},
                     success: function (response) {
                         if (response.errno == '0') {
                             $(".orders-list>li[order-id=" + orderId + "]>div.order-content>div.order-text>ul li:eq(4)>span").html("已拒单");
                             $("ul.orders-list>li[order-id=" + orderId + "]>div.order-title>div.order-operate").hide();
                             $("#accept-modal").modal("hide");
                             $("#reject-modal").modal("show");
                         } else {
                             alert(response.errmsg)
                         }


                     }


                 });
             });
        } else {

            alert(data.errmsg)
        }
    });


});
