# -*- coding:utf-8 -*-

from . import api
from flask import  request,make_response,jsonify,current_app
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome import constants
from ihome.utils.response_code import RET



@api.route('/image_code')
def get_image_code():
    uuid = request.args.get('uuid')
    pre_uuid = request.args.get('pre_uuid')
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

@api.route('/sms_codes')
def sms_code():
    pass




@api.route('/register')
def register():
    pass
