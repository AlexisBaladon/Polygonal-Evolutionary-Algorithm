from PIL import Image
import io
import base64
import re

from flask import Request


def transform(request: Request):
    image_file = request.files['image']

    if image_file is not None:
        try:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            img_tag = f"<img src='data:image/{image_file.content_type};base64,{image_base64}' width='250px'>"
            return img_tag
        except Exception as e:
            return str(e)
    return "No image received :("