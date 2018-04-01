# -*- coding:utf-8 -*-

import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import configs


db = SQLAlchemy()
redis_store = None


def get_app(config_name):
    app = Flask(__name__)
    # 配置
    app.config.from_object(configs.get(config_name))
    # 数据库
    db.init_app(app)
    # 全局可用的redis
    global redis_store
    redis_store = redis.StrictRedis(host=configs.get(config_name).REDIS_HOST, port=configs.get(config_name).REDIS_PORT)
    # 开启 csrf 保护
    CSRFProtect(app)
    # 开启Session
    Session(app)


    return app