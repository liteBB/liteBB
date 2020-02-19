# -*- coding: utf-8 -*-

import os
from flask import Flask, g
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_pagedown import PageDown
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from config import config
from config import basedir
from .utils import create_folder


db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection = 'basic'  # also can be 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = None
csrf = CSRFProtect()
babel = Babel()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    babel.init_app(app)

    create_folder(os.path.join(basedir, 'app', 'static', 'upload'))
    create_folder(os.path.join(basedir, 'app', 'static', 'image', 'photo'))
    create_folder(os.path.join(basedir, 'app', 'static', 'video'))
    create_folder(os.path.join(basedir, 'app', 'static', 'attachment'))

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app


@babel.localeselector
def get_locale():
    return g.language.replace('-', '_')


