from src.models.evolutionary_algorithm.ea_handler import EAHandler

from flask import Flask
# from celery import Celery

from server import config

REDIS_URL = "redis://localhost:6379/0"

class UserContext:
    def __init__(self, user_eac: EAHandler=None, 
                 encoded_images = [],
                 decoded_image = None,
                 args: dict = None):
        self.user_eac = user_eac
        self.encoded_images = encoded_images
        self.args = args
        self.decoded_image = decoded_image

    def __repr__(self):
        return f"UserContext(user_eac={self.user_eac}, encoded_images={self.encoded_images}, decoded_image={self.decoded_image}, args={self.args})"
    
    def __str__(self):
        return repr(self)

def create_app(development=False):
    app = Flask(__name__, 
                template_folder='modules', 
                static_url_path='/static')
    
    app.config['DEBUG'] = development
    app.config['SECRET_KEY'] = config.secret_key

    return app

app = create_app(development=not config.production)
# app.config.from_mapping(
#     CELERY=dict(
#         broker_url=REDIS_URL,
#         result_backend=REDIS_URL,
#         task_ignore_result=True
#     )
# )

from server import modules