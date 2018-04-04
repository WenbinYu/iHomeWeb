# -*- coding:utf-8 -*-

from flask import Blueprint,current_app,make_response
from flask_wtf.csrf import generate_csrf

html_blue = Blueprint('html_blue',__name__)


@html_blue.route('/<re(".*"):filename>')
def get_static_html(filename):
    if not filename:
        filename = 'index.html'
    if not filename.endswith('.html'):
        if filename != 'favicon.ico' and filename != 'html/index.html':
            filename = 'html/'+ filename + '.html'
    else:
        filename = 'html/' + filename
    csrf_token = generate_csrf()
    # 将 csrf_token 设置到 cookie 中
    response = make_response(current_app.send_static_file(filename))
    response.set_cookie("csrf_token", csrf_token)
    return response