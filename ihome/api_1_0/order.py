# -*- coding:utf-8 -*-
import datetime

from . import api
from ihome.utils.common import login_requseted,jsonify
from flask import request,current_app,g
from ihome.utils.response_code import RET
from ihome.models import User,House,Order
from ihome import db,redis_store


@api.route('/orders',methods= ['POST'])
@login_requseted
def create_order():
    req = request.json
    if not req:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    house_id= req.get('house_id')
    sd = req.get('sd')
    ed = req.get('ed')
    if not all([house_id,sd,ed]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    try:
        start_date = datetime.datetime.strptime(sd, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(ed, '%Y-%m-%d')
        # 自己校验入住时间是否小于离开的时间
        if start_date and end_date:
            # 断言：入住时间一定小于离开时间，如果不满足，就抛出异常
            assert start_date < end_date, Exception('入住时间有误')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='入住时间有误')

    user_id = int(g.user_id)
    try:
        user = User.query.get(user_id)
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
        # 如果用户不存在
    if user is None:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    if house is None:
        return jsonify(errno=RET.DATAERR, errmsg='房屋信息不存在')
    if house.user_id == user_id:
        return jsonify(errno=RET.PARAMERR, errmsg='房主请求自己房间')
    try:
        order_list = Order.query.filter(end_date > Order.begin_date, start_date < Order.end_date,Order.house_id ==house_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='请求的订单信息有误')
    if order_list:
        return jsonify(errno=RET.PARAMERR, errmsg='房屋已被预定')
    days = (end_date - start_date).days
    order = Order()
    order.user_id =user_id
    order.house_id =house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = days
    order.house_price = house.price
    order.amount = days*house.price
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存订单数据失败')

        # 6.响应结果
    return jsonify(errno=RET.OK, errmsg='OK')



@api.route('/orders',methods = ['PUT','GET'])
@login_requseted
def search_order():
    user_id = int(g.user_id)
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
    if user is None:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    if request.method == 'GET':
        role = request.args.get('role')
        if not role:
            return jsonify(errno=RET.PARAMERR, errmsg='缺少请求主体')
        if role not in ['custom','landlord']:
            return jsonify(errno=RET.PARAMERR, errmsg='请求参数不符合规则')
        try:
            if role == 'custom':
                orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc()).all()
            else:
                houses = House.query.filter(House.user_id == user_id).all()
                orders = Order.query.filter(Order.house_id.in_([house.id for house in houses])).order_by(Order.create_time.desc()).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='订单查询失败')


        if not orders:
            return jsonify(errno=RET.NODATA, errmsg='暂无订单信息')
        orders_list = []
        for order in orders:
            orders_list.append(order.to_dict())
        return jsonify(errno=RET.OK, errmsg='OK',resp = orders_list)

    if request.method == 'PUT':
        req = request.json
        if not req:
            return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
        order_id = req.get('order_id')
        comment = req.get('comment')
        if not all([order_id,comment]):
            return jsonify(errno=RET.PARAMERR, errmsg='缺少请求参数')
        try:
            order = Order.query.filter(Order.user_id == user_id,Order.id == order_id,Order.status=='WAIT_COMMENT').first()
            house = order.house
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询订单出错')
        order.comment = comment
        order.status = 'COMPLETE'
        house.order_count += 1

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg='信息保存错误')
        # 删除redis中缓存的房屋详情信息,因为房屋详情信息已经更新
        # try:
        #     redis_store.delete('house_info_' + house.id)
        # except Exception as e:
        #     current_app.logger.error(e)
        return jsonify(errno=RET.OK, errmsg='OK')



@api.route('/orders/status',methods=['PUT'])
@login_requseted
def accept_order():
    user_id = int(g.user_id)
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
    if user is None:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    action = request.args.get('action')
    if not action:
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数不合法')
    order_id = request.json.get('order_id')

    if not order_id:
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数缺失')
    try:
        order = Order.query.filter(Order.id == order_id,Order.status == 'WAIT_ACCEPT').first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='请求订单查询错误')
    if not order:
        return jsonify(errno=RET.DATAERR, errmsg='订单不存在')
    if house.user_id != user_id:
        return jsonify(errno=RET.DATAERR, errmsg='请求的房屋信息有误')
    if action == 'accept':
        order.status = 'WAIT_COMMENT'
    else:
        order.status = 'REJECTED'
        comment = request.json.get('comment')
        if not comment:
            return jsonify(errno=RET.PARAMERR, errmsg='请求参数缺失')
        order.comment = comment
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据保存错误')
    return jsonify(errno=RET.OK, errmsg='OK')


