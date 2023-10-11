from flask import Blueprint

from api import app
from api.modules.transform.transform_router import transform_blueprint

def register_blueprint(blueprint: Blueprint, url_prefix=None, app=app):
    app.register_blueprint(blueprint, url_prefix=url_prefix)

register_blueprint(transform_blueprint, url_prefix='/api/transform')