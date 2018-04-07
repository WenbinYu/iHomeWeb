# -*- coding:utf-8 -*-

from . import api
from flask import current_app,session,request,jsonify,g
from ihome.models import Area,HouseImage,House, User
from ihome import redis_store,db
from ihome.utils.response_code import RET
from ihome import constants
from ihome.utils.common import login_requseted

@api.route('/areas')
def get_areas():
    """提供城区信息
    1.查询所有的城区信息
    2.构造响应数据
    3.响应结果
    """
    # 查询缓存数据，如果有缓存数据，就使用缓存数据，反之，就查询，并缓存新查询的数据
    try:
        area_dict_list = redis_store.get('Areas')
        if area_dict_list:
            return jsonify(errno=RET.OK, errmsg='OK', data=eval(area_dict_list))
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
    return jsonify(errno=RET.OK, errmsg='OK', data=area_dict_list)


@api.route('/houses')
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


