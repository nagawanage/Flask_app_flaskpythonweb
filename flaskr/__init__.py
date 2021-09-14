# __ init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flaskr.utils.template_filters import replace_newline
from .config.settings import DevelopConfig, ProdConfig

# Flask-Loginライブラリとアプリケーションをつなぐ
login_manager = LoginManager()
# ログインの関数
login_manager.login_view = 'app.view'
# ログインにリダイレクトした際のメッセージ
login_manager.login_message = 'ログインしてください'

basedir = os.path.abspath(os.path.dirname(__name__))
db = SQLAlchemy()
migrate = Migrate()
# config = {
#     'develop': 'config/develop/settings.cfg',
#     'prod': 'config/prod/settings.cfg'
# }
config_class = {
    'develop': DevelopConfig,
    'prod': ProdConfig
}


def create_app():
    app = Flask(__name__)
    """config from dict"""
    # config_file = config[os.getenv('ENVIRONMENT', 'develop')]
    # app.config.from_pyfile(config_file)
    # print(f'{config_file=}')
    """config from env"""
    # app.config.from_envvar('FLASK_CONFIG_ENV')
    """config from class"""
    config_target = config_class[os.getenv('ENVIRONMENT', 'develop')]
    app.config.from_object(config_target)

    from flaskr.views import bp
    app.register_blueprint(bp)
    app.add_template_filter(replace_newline)  # 自作フィルタを追加
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    return app
