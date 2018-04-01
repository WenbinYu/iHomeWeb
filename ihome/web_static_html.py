# -*- coding:utf-8 -*-

from flask import Blueprint,current_app


html_blue = Blueprint('html_blue',__name__)


@html_blue.route('/<re(".*"):filename>')
def get_static_html(filename):
    if not filename:
        filename = '/index.html'

    if filename != 'favicon.ico':
        filename = 'html/'+ filename

    return current_app.send_static_file(filename)
