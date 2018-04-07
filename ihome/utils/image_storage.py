# -*- coding:utf-8 -*-

from qiniu import Auth,put_data
from ihome.constants import QINIU_DOMIN_PREFIX,QINIU_ACCESS_KEY,QINIU_BUCKET_HOME,QINIU_SECRET_KEY
from flask import current_app

def upload_image(data):
    if not data:
        return  None
    try:
        q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        token = q.upload_token(QINIU_BUCKET_HOME)

        ret, info = put_data(token,None,data)
    except Exception as e:
        current_app.logger.error(e)
        raise e

    if info and info.status_code != 200:
        raise Exception("上传文件到七牛失败")
    return ret.get('key')



if __name__ == '__main__':
    path = '/home/python/Desktop/fruit.jpg'
    with open(path, 'rb') as file:
        upload_image(file.read())