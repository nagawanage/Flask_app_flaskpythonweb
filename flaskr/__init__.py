# flaskr/__init__.py
from flask import Flask


# BluePrintをimport
def create_app():
    app = Flask(__name__)
    from flaskr.mysite1.views import mysite1_bp
    from flaskr.mysite2.views import mysite2_bp
    # BluePrintを登録
    app.register_blueprint(mysite1_bp)
    app.register_blueprint(mysite2_bp)
    return app
