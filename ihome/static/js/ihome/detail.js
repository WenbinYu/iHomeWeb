function hrefBack() {
    history.go(-1);
}

// 解析提取url中的查询字符串参数
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function swiper() {
    //  数据加载完毕后,需要设置幻灯片对象，开启幻灯片滚动
    var mySwiper = new Swiper ('.swiper-container', {
        loop: true,
        autoplay: 2000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationType: 'fraction'
    });
}

$(document).ready(function(){
    // 获取详情页面要展示的房屋编号
    var queryData = decodeQuery();
    var houseId = queryData["id"];

    //  获取该房屋的详细信息
    $.get('/api/1.0/house/detail/'+ houseId, function (data) {
        if ('0' == data.errno) {
            var list_html = template('house-image-tmpl', {img_urls: data.resp.house_dict.img_urls,price:data.resp.house_dict.price});
            $('.swiper-container').html(list_html);

            swiper();

            var list_html1 = template('house-detail-tmpl', {house: data.resp.house_dict});
            $('.detail-con').html(list_html1);

             if (data.resp.user_id && data.resp.user_id == data.resp.house_dict.user_id){
                 $('.book-house').hide();
             }else {
                    $('.book-house').show();
                    $('.book-house').attr('href','booking.html?hid=' + data.resp.house_dict.hid);
             }

        } else {
            alert(data.errmsg);

        }
    });

    //  数据加载完毕后,需要设置幻灯片对象，开启幻灯片滚动

});