"""
% export ENVIRONMENT=<develop|prod>
"""
import os


class DevelopConfig:
    basedir = os.path.abspath(os.path.dirname(__name__))
    SECRET_KEY = 'mysite'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data_develop.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'development'


class ProdConfig:
    basedir = os.path.abspath(os.path.dirname(__name__))
    SECRET_KEY = 'mysite'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data_prod.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'production'
