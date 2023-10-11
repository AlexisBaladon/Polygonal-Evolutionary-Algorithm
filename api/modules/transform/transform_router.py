import base64
from io import BytesIO
from PIL import Image

from flask import Blueprint, request

from api.modules.transform import transform_controller

transform_blueprint = Blueprint("transform", __name__)

@transform_blueprint.route("", methods=['GET'])
def transform():
        return """
    <!DOCTYPE html>
        <html>
        <head>
            <title>Image Submission Form</title>
        </head>
        <body>
            <h1>Submit an Image</h1>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*">
                <button type="submit">Submit</button>
            </form>
        </body>
        </html>
"""

@transform_blueprint.route("", methods=['POST'])
def transform():
    transform_controller.transform(request)