# -*- coding:utf-8 -*-
import datetime

from . import api
from flask import current_app,session,request,jsonify,g
from ihome.models import Area,HouseImage,House, User,Facility,Order
from ihome import redis_store,db
from ihome.utils.response_code import RET
from ihome import constants
from ihome.utils.common import login_requseted
from ihome.utils.image_storage import upload_image
from ihome import constants
import time



@api.route('/areas')
def get_areas():
    # 查询缓存数据，如果有缓存数据，就使用缓存数据，反之，就查询，并缓存新查询的数据
    try:
        area_dict_list = redis_store.get('Areas')
        if area_dict_list:
            return jsonify(errno=RET.OK, errmsg='OK', areas=eval(area_dict_list))
    except Exception as e:
        current_app.logger.error(e)
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询城区信息失败')
    # 2.构造响应数据
    area_dict_list = []
    for area in areas:
        area_dict_list.append(area.to_dict())

    # 缓存城区信息到redis : 没有缓存成功也没有影响，因为前爱你会判断和查询
    try:
        redis_store.set('Areas', area_dict_list, constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
    # 3.响应结果
    return jsonify(errno=RET.OK, errmsg='OK', areas=area_dict_list)


@api.route('/houses',methods = ['POST'])
@login_requseted
def public_house():
    user_id = int(g.user_id)
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
        # 如果用户不存在
    if user is None:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    # if request.method == 'GET':
    #     pass
    house_dict = request.json
    if not house_dict:
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    title = house_dict.get('title')
    price = house_dict.get('price')
    address = house_dict.get('address')
    area_id = house_dict.get('area_id')
    room_count = house_dict.get('room_count')
    acreage = house_dict.get('acreage')
    unit = house_dict.get('unit')
    capacity = house_dict.get('capacity')
    beds = house_dict.get('beds')
    deposit = house_dict.get('deposit')
    min_days = house_dict.get('min_days')
    max_days = house_dict.get('max_days')

    if not all(
            [title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    try:
        price = int(float(price)* 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='传入参数错误')

    house = House()
    house.user_id = user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    facility = house_dict.get('facility')
    if facility:
        facilities = Facility.query.filter(Facility.id.in_(facility)).all()
        house.facilities = facilities
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存房屋信息失败')
    return jsonify(errno=RET.OK, errmsg='OK',house_id = house.id)


@api.route('/house/images',methods = ['POST'])
@login_requseted
def set_house_image():
    user_id = int(g.user_id)
    try:
        image_files = request.files.get('house_image')
        house_id = request.form.get('house_id')
    except Exception as  e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数错误')
    if not all([house_id,image_files]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少请求参数')
    try:
        house = House.query.get(int(house_id))
        if not house:
            return jsonify(errno=RET.DATAEXIST, errmsg='请求参数信息错误')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')
    try:
        image_key = upload_image(image_files.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='图片上传错误')
    if not image_key:
        return jsonify(errno=RET.DATAERR, errmsg='图片信息错误')
    if not house.index_image_url:
        house.index_image_url = image_key
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = image_key
    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据库错误')
    image_url = constants.QINIU_DOMIN_PREFIX + image_key
    return jsonify(errno=RET.OK, errmsg='OK', image_url= image_url)



@api.route('/house/detail/<int:house_id>')
def house_detail(house_id):
    if not house_id:
        return jsonify(errno=RET.DATAEXIST, errmsg='缺少参数')
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='请求参数信息错误')
    if not house:
        return jsonify(errno=RET.DATAEXIST, errmsg='房屋信息不存在')
    user_id = session.get('user_id')
    house_dict = house.to_full_dict()
    resp = {
        'house_dict':house_dict,
        'user_id':user_id
    }
    return jsonify(errno=RET.OK, errmsg='OK',resp =resp)


@api.route('/index/house_image')
def get_house_image():
    try:
        index_houses = redis_store.get('Index_images_info')
        if index_houses:
            return jsonify(errno=RET.OK, errmsg='OK',index_houses = eval(index_houses))
    except Exception as e:
        current_app.logger.error(e)

    try:
        houses = House.query.filter(House.index_image_url != '').order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询失败')
    if not houses:
        return jsonify(errno=RET.DBERR, errmsg='数据错误')
    index_houses = []
    for house in houses:
        index_houses.append(house.to_basic_dict())
    try:
        redis_store.set('Index_images_info',index_houses,constants.HOME_PAGE_DATA_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg='OK',index_houses = index_houses)


@api.route('/houses/list')
def search_house():
    req = request.args
    area_id = req.get('aid', '')
    start_date_str = req.get('sd', '')
    end_date_str = req.get('ed', '')
    # booking(订单量), price-inc(低到高), price-des(高到低),
    sort_key = req.get('sk', 'new')
    page = req.get('p', '1')
    try:
        page = int(page)
        start_date = None
        end_date = None
        if start_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        if end_date and start_date:
            assert end_date > start_date ,Exception('开始时间大于结束时间')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='请求参数有错误')

    house_query = House.query
    try:
        if area_id:
            house_query = house_query.filter(House.area_id == int(area_id))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='请求参数有错误')
    order_list = []
    if end_date and start_date:
        order_list = Order.query.filter(end_date > Order.begin_date,start_date < Order.end_date).all()
    elif start_date:
        order_list = Order.query.filter(start_date < Order.end_date).all()
    elif end_date:
        order_list =Order.query.filter(end_date > Order.begin_date).all()
    if order_list:
        order_list_house = [order.house_id for order in order_list]

        house_query = house_query.filter(House.id.notin_(order_list_house) )

    if sort_key == 'booking':
        house_query = house_query.order_by(House.order_count.desc())
    elif sort_key == 'price-inc':
        house_query = house_query.order_by(House.price)
    elif sort_key == 'price-des':
        house_query = house_query.order_by(House.price.desc())
    else:
        house_query = house_query.order_by(House.create_time.desc())

        # 使用paginate进行分页
    house_pages = house_query.paginate(page, constants.HOUSE_LIST_PAGE_CAPACITY, False)
    # 获取当前页对象
    houses = house_pages.items
    # 获取总页数
    total_page = house_pages.pages

    house_dict = []
    for house in houses:
        house_dict.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg='请求成功', resp={"total_page": total_page, "houses": house_dict})







