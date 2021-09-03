"""
Usage:
    % python model.py
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, CheckConstraint

base_dir = os.path.dirname(__file__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)  # SQLAlchemyを扱うためのインスタンス作成


class Person(db.Model):
    __tablename__ = 'persons'
    __tableargs__ = (CheckConstraint('updated_at >= created_at'))  # チェック制約

    id = db.Column(db.Integer, primary_key=True)  # 主キー
    name = db.Column(db.String(20), index=True, server_default='nanashi')  # デフォルト値
    phone_number = db.Column(db.String(13), nullable=False, unique=True)  # NOT NULL, UNIQUE
    age = db.Column(db.Integer, nullable=False)  # NOT NULL
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, name, phone_number, age, created_at, updated_at):
        self.name = name
        self.phone_number = phone_number
        self.age = age
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f'{self.id=}, {self.name=}, {self.phone_number=}, {self.age=}, \
                    {self.created_at=}, {self.updated_at=}'


# 関数インデックス（指定した関数の計算結果に対しての検索を早くする）
db.Index('my_index', func.lower(Person.name))  # lower(name)

# 作成
db.create_all()
