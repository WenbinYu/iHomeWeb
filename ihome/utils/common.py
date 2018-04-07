# -*- coding:utf-8 -*-

from flask import session,jsonify,g ,request
from werkzeug.routing import BaseConverter
from functools import wraps
from ihome.utils.response_code import RET

class RegexConverter(BaseConverter):

    def __init__(self,url_map,*args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def login_requseted(view_func):

    @wraps(view_func)
    def wrapper( *args,**kwargs):
        next_url = request.url
        user_id = session.get('user_id')
        # g.next_url = next_url
        if not user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录',next_url = next_url)
        g.user_id = user_id
        return view_func(*args,**kwargs)
    return wrapper

