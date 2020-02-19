# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

APP_TITLE = 'liteBB'
DOMAIN_NAME = 'litebb.com'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    WTF_CSRF_TIME_LIMIT = 21600
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    LISTS_PER_PAGE = 10
    SUMMARY_COUNT = 140
    SLOW_DB_QUERY_TIME = 0.5
    MAX_CONTENT_LENGTH = 1000 * 1024 * 1024

    ACCEPT_LANGUAGES = ['en', 'zh-CN']

    @staticmethod
    def init_app(app):
        pass

class ProductionConfig(Config):

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'litebb.sqlite')
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:passwd@localhost:3306/litebb?charset=utf8mb4'


class DevelopmentConfig(Config):

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'litebb_dev.sqlite')

config = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'default': ProductionConfig
}
