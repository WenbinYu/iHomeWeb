# -*- coding:utf-8 -*-

import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import configs
from ihome.utils.common import RegexConverter
import logging
from logging.handlers import RotatingFileHandler



db = SQLAlchemy()
redis_store = None
csrf = CSRFProtect()
#

def set_log(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(asctime)s-%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)



def get_app(config_name):
    set_log(configs.get(config_name).level)

    app = Flask(__name__)
    # 配置
    app.config.from_object(configs.get(config_name))
    # 数据库
    db.init_app(app)
    # 全局可用的redis
    global redis_store
    redis_store = redis.StrictRedis(host=configs.get(config_name).REDIS_HOST, port=configs.get(config_name).REDIS_PORT)
    # 开启 csrf 保护
    csrf.init_app(app)
    # 开启Session
    Session(app)

    app.url_map.converters['re'] = RegexConverter

    from .api_1_0 import api
    app.register_blueprint(api)

    from ihome.web_static_html import html_blue
    app.register_blueprint(html_blue)

    return app