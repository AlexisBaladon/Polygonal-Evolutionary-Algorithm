import json

from flask_redis import FlaskRedis
from server import app
#from flask import g

def create_broker(app=app):
    return FlaskRedis(app)

broker = create_broker()

def set(key: str, value, object=True):
    if object:
        value = json.dumps(value)

    broker.set(key, value)
    
    # with app.app_context():
    #     setattr(g, key, value)

    return

def get(key: str, object=True):
    value = broker.get(key)

    # with app.app_context():
    #     value = getattr(g, key)

    if object and value is not None:
        value = json.loads(value)

    return value

def get_added_image_key(user_id: str, i: int):
    return f"added_image/{user_id}/{i}"

def get_last_connection_key(user_id: str):
    return f"last_connection/{user_id}"