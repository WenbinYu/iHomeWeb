# -*- coding:utf-8 -*-


import random
import re
from . import api
from flask import  request,make_response,jsonify,current_app,session,g
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store,db
from ihome import constants
from ihome.utils.response_code import RET
from ihome.utils.SMS import CCP
from ihome.models import User
from ihome.utils.common import login_requseted




@api.route('/image_code')
def get_image_code():
    uuid = request.args.get('uuid')
    pre_uuid = request.args.get('pre_uuid')
    if not uuid:
        return jsonify(errno=RET.REQERR, errmsg='请求参数不全')
    # 生成验证码
    name, text, image = captcha.generate_captcha()
    # 存储到redis中
    current_app.logger.debug(text)
    try:
        redis_store.delete("ImageCode:"+pre_uuid)
        redis_store.setex('ImageCode:' + uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))
    else:
        resp = make_response(image)
        # 设置内容类型
        resp.headers['Content-Type'] = 'image/jpg'
        return resp

@api.route('/sms_codes', methods=['POST'])
def sms_code():
    resq = request.json
    if not resq:
        return jsonify(errno=RET.NODATA, errmsg='数据不存在')
    mobile = resq.get('mobile')
    uuid = resq.get('uuid')
    imagecode = resq.get('imageCode')

    if not all([mobile,uuid,imagecode]):
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数不全')
    # 验证手机号是否合法
    if not re.match(r"^1[34578][0-9]{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号不合法')
    try:
        sever_image_code = redis_store.get('ImageCode:' + uuid)
    except Exception as e:
         current_app.logger.error(e)
         return jsonify(errno=RET.DBERR, errmsg='图片验证码获取失败')
    if not sever_image_code:
         return jsonify(errno=RET.DBERR, errmsg='图片验证码不存在')
    if sever_image_code.lower() != imagecode.lower():
         return jsonify(errno=RET.DATAERR , errmsg='图片验证码错误')
    mobile_sms_code = '%06d' % random.randint(0,999999)
    current_app.logger.debug(mobile_sms_code)
    # result = CCP().send_sms(mobile,[mobile_sms_code,constants.SMS_CODE_REDIS_EXPIRES / 60],'1')
    result = 0
    if result == 0:
        try:
            redis_store.delete('ImageCode:' + uuid)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg='删除本地图片验证码失败')
        try:
            redis_store.setex('mobile:' + mobile, constants.IMAGE_CODE_REDIS_EXPIRES, mobile_sms_code)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='短信验证码存储失败')
        return jsonify(errno=RET.OK, errmsg='发送验证码成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送验证码失败')






@api.route('/users', methods=['POST'])
def register():
    resq = request.json
    if not resq:
        return jsonify(errno=RET.PARAMERR, errmsg='请求参数缺失')
    mobile = resq.get('mobile')
    clien_sms_code = resq.get('smscode')
    password = resq.get('password')

    if not all([mobile,clien_sms_code,password]):
        return jsonify(errno=RET.DATAERR, errmsg='请求参数不全')
    try:
        user = User.query.filter_by(mobile = mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='校对用户表失败')
    if user:
         return jsonify(errno=RET.DATAERR, errmsg='用户已注册')
    try:
        server_sms_code = redis_store.get('mobile:'+mobile)
    except Exception as e:
         current_app.logger.error(e)
         return jsonify(errno=RET.DBERR, errmsg='查询短信验证码失败')
    if not server_sms_code:
        return jsonify(errno=RET.DATAEXIST, errmsg='短信验证码失效')
    if server_sms_code != clien_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码不正确')
    try:
        redis_store.delete('mobile:'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='删除短信验证码失败')
    # user = User(name=mobile, mobile=mobile)
    user = User()
    user.name = mobile
    user.mobile = mobile
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='写入用户表错误')
    session['name'] = user.name
    session['user_id'] = user.id
    session['mobile'] = mobile
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/sessions', methods=["POST"])
def login():
    resq = request.json
    next_url = request.args.get('next','/')
    print next_url
    if not resq:
        return jsonify(errno=RET.NODATA, errmsg='请求参数错误')
    mobile = resq.get('mobile')
    password = resq.get('password')
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR, errmsg='用户参数不全')
    try:
        user = User.query.filter_by(mobile = mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='校对用户信息出错')
    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户名或密码错误')
    if user.check_password(password):
        session['user_id'] = user.id
        session['name'] = user.name
        session['mobile'] = mobile

        return jsonify(errno=RET.OK, errmsg='OK',next_url = next_url)


    return jsonify(errno=RET.PARAMERR, errmsg='用户名或密码错误')




@api.route('/sessions' ,methods = ['DELETE'])
@login_requseted
def logout():
    user_id = int(g.user_id)
    user = User.query.get(user_id)
    session.pop('user_id')
    session.pop('name')
    session.pop('mobile')
    return jsonify(errno=RET.OK, errmsg='登出成功')




