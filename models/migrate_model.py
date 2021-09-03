"""
Usage:
    % cd models/
    % export FLASK_APP=migrate_model.py
    % flask db init
        - migrationsフォルダが作成される
    % flask db migrate -m "add Person"
    % flask db upgrade
        - migrate_data.sqlite 作成

    - class Person にgender追加 -
    % flask db migrate -m "add gender to Person"
    % flask db upgrade
        select * from alembic_version; でDBバージョン確認
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


base_dir = os.path.dirname(__file__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'migrate_data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # データベースの変更追跡管理
db = SQLAlchemy(app)  # SQLAlchemyを扱うためのインスタンス作成
Migrate(app, db)


class Person(db.Model):
    __tablename__ = 'persons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    gender = db.Column(db.Text)  # add -> % flask db migrate -m "add gender to Person"
    age = db.Column(db.Integer)

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        # インスタンス作成時に値設定
        return f'id = {self.id}, name={self.name}, age={self.age}'
