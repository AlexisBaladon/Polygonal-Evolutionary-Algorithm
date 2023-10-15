from flask import Blueprint

from api.modules.app import app_controller

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route("/")
def index():
    return app_controller.index()