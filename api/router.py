from flask import Blueprint

from api import app
from api.modules.transform.transform_router import transform_blueprint
from api.modules.app.app_router import main_blueprint

def register_blueprint(blueprint: Blueprint, url_prefix=None, app=app):
    app.register_blueprint(blueprint, url_prefix=url_prefix)

def initialize():
    register_blueprint(main_blueprint)
    register_blueprint(transform_blueprint, url_prefix='/transform')