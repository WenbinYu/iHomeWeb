# -*- coding:utf-8 -*-

from flask import g,session,jsonify,request,current_app

from ihome import constants
from . import api
from ihome import db,redis_store
from ihome.utils.common import login_requseted
from ihome.models import User
from ihome.utils.response_code import RET
from ihome.utils.image_storage import upload_image


@api.route('/users',methods = ['GET'])
@login_requseted
def get_user_profile():
    user_id = int(g.user_id)
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
        # 如果用户不存在
    if user is None:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    user_dict = user.to_dict()
    return jsonify(errno=RET.OK, errmsg='OK',user_dict = user_dict)


@api.route('/users/avatar',methods=['POST'])
@login_requseted
def upload_avatar():
    user_id = int(g.user_id)
    try:
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数错误')
    if not avatar_file:
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数不全')
    image_key = upload_image(avatar_file)
    if not image_key:
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片系统错误')
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
    if user is None:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    user.avatar_url = image_key
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='上传数据库错误')
    avatar_url = constants.QINIU_DOMIN_PREFIX + image_key
    return jsonify(errno=RET.OK, errmsg='OK',avatar_uravl= avatar_url)


@api.route('/users/name',methods = ['PUT'])
@login_requseted
def set_user_profile():
    user_id = int(g.user_id)
    new_name = request.json.get('new_name')
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
        # 如果用户不存在
    if user is None:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    if not new_name:
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数不全')
    if user.name == new_name:
        return jsonify(errno=RET.PARAMERR, errmsg='用户名已存在')
    user.name = new_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据保存错误')
    session['nmae'] = new_name
    return jsonify(errno=RET.OK, errmsg='OK')

@api.route('/users/auth',methods =['POST','GET'])
@login_requseted
def set_auth_name():
    user_id = int(g.user_id)
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')
        # 如果用户不存在
    if user is None:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    if request.method == 'GET':
        auth_dict = user.to_author_dict()
        return jsonify(errno=RET.OK, errmsg='OK',auth_dict = auth_dict)

    real_name = request.json.get('real_name')
    id_card = request.json.get('id_card')
    if not all([real_name,id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数不全')

    if user.real_name and user.id_card:
        return jsonify(errno=RET.REQERR, errmsg='非法请求')
    user.real_name = real_name
    user.id_card = id_card
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据保存错误')
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/users/sessions')
def get_sessions():
    user_id = session.get("user_id")
    name = session.get('name')
    mobile = session.get('mobile')

    if not all([user_id,name,mobile]):
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    resp = {
        'user_id':user_id,
        'name':name,
        'mobile':mobile
    }
    return jsonify(errno=RET.OK, errmsg='OK',resp =resp)


