from flask import Blueprint, request

from server.modules.transform import transform_controller

transform_blueprint = Blueprint("transform", __name__)

@transform_blueprint.route("", methods=['POST'])
def transformed_image():
    return transform_controller.transform(request)

@transform_blueprint.route("", methods=['GET'])
def get_transformed_image():
    return transform_controller.get_transformed_images(request)